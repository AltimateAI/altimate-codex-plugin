import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HOOKS = Path(__file__).resolve().parents[1]/'plugins/altimate-code/hooks'
spec = importlib.util.spec_from_file_location('refresh', HOOKS/'refresh-workspace-skills.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='skill refresh ')
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)/'project'
        self.project.mkdir()
        (self.project/'.altimate-code').mkdir()
        self.bin = Path(self.tmp.name)/'bin'
        self.bin.mkdir()
        self.log = self.project/'refresh.log'
        cli = self.bin/'altimate-code'
        cli.write_text(f'''#!{sys.executable}
import os, pathlib, sys, time
assert sys.argv[1:4] == ['workspace', 'refresh', '--directory']
p=pathlib.Path(sys.argv[4])
assert p.resolve() == pathlib.Path.cwd().resolve()
with (p/'refresh.log').open('a') as f: f.write('start\\n')
time.sleep(float(os.environ.get('REFRESH_TEST_DELAY','0')))
if os.environ.get('REFRESH_TEST_FAIL'): sys.exit(7)
stamp=p/'.altimate-code/skill/_workspace/.synced-at'
stamp.parent.mkdir(parents=True,exist_ok=True)
stamp.touch()
with (p/'refresh.log').open('a') as f: f.write('done\\n')
''')
        cli.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin)+os.pathsep+os.environ['PATH'])
        self.env.pop('ALTIMATE_CODEX_SKILL_SYNC', None)

    def run_hook(self, mode='--wait', **env):
        return subprocess.run(['bash', str(HOOKS/'refresh-skills.sh'), mode],
                              cwd=self.tmp.name, input=json.dumps({'cwd': str(self.project)}),
                              env={**self.env, **env}, text=True, capture_output=True, timeout=8)

    def wait_done(self):
        deadline = time.monotonic()+5
        while time.monotonic()<deadline:
            if self.log.exists() and 'done' in self.log.read_text():
                return
            time.sleep(.03)
        self.fail('background refresh did not complete')

    def test_manual_refresh_and_failed_refresh(self):
        result=self.run_hook()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('.agents/skills: 0',result.stdout)
        self.assertEqual(self.run_hook(REFRESH_TEST_FAIL='1').returncode,7)

    def test_startup_is_nonblocking_and_stop_single_flight(self):
        start=time.monotonic()
        result=self.run_hook('--startup',REFRESH_TEST_DELAY='1.5')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertLess(time.monotonic()-start,1.2)
        self.assertNotIn('done',self.log.read_text() if self.log.exists() else '')
        self.run_hook('--if-stale')
        self.wait_done()
        self.assertEqual(self.log.read_text().splitlines(),['start','done'])
        self.run_hook('--if-stale')
        self.assertEqual(self.log.read_text().splitlines(),['start','done'])

    def test_opt_out_and_no_state(self):
        result=self.run_hook(ALTIMATE_CODEX_SKILL_SYNC='0')
        self.assertEqual(result.returncode,0)
        self.assertFalse(self.log.exists())
        (self.project/'.altimate-code').rmdir()
        self.assertEqual(self.run_hook().returncode,0)
        self.assertFalse(self.log.exists())

    def test_wait_never_steals_busy_lock(self):
        lock=self.project/'.altimate-code/codex-skill-refresh.lock'
        with lock.open('w') as f, patch.dict(os.environ,self.env,clear=True), patch.object(refresh,'WAIT_SECONDS',.05):
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(refresh.refresh(self.project,wait=True),1)
            self.assertFalse(self.log.exists())

    def test_staleness_boundary_and_future_stamp(self):
        stamp=self.project/'.altimate-code/skill/_workspace/.synced-at'
        stamp.parent.mkdir(parents=True);stamp.touch()
        for age,expected in [(3599,True),(3600,False),(-1,False)]:
            os.utime(stamp,(10000-age,10000-age))
            with patch.object(refresh.time,'time',return_value=10000):
                self.assertEqual(refresh.fresh(self.project),expected)

    def test_symlink_destination_and_timeout(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir()
        (self.project/'.agents').symlink_to(outside,target_is_directory=True)
        self.assertNotEqual(self.run_hook().returncode,0)
        self.assertEqual(list(outside.iterdir()),[])
        self.assertFalse(self.log.exists())
        (self.project/'.agents').unlink()
        with patch.dict(os.environ,self.env,clear=True), patch.object(refresh,'WAIT_SECONDS',.05):
            with patch.dict(os.environ,{'REFRESH_TEST_DELAY':'1'}):
                with self.assertRaises(subprocess.TimeoutExpired):
                    refresh.refresh(self.project,wait=True)

    def test_startup_hook_manifest_wiring(self):
        hooks=json.loads((HOOKS/'hooks.json').read_text())['hooks']
        self.assertIn('--if-stale',hooks['Stop'][0]['hooks'][0]['command'])
        result=subprocess.run(['bash',str(HOOKS/'altimate-code-session-start.sh')],cwd=self.tmp.name,
                              input=json.dumps({'cwd':str(self.project)}),env=self.env,text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.wait_done()

    def tenant_fixture(self):
        spec=importlib.util.spec_from_file_location('test_mirror',HOOKS/'sync-workspace-skills.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        creds=self.project/'fixture-account.json'
        m.CREDENTIALS=str(creds)
        creds.write_text(json.dumps({'altimateInstanceName':'first','altimateUrl':'https://example.invalid'}))
        snapshot=self.project/'.altimate-code/skill/_workspace'
        (snapshot/'id').mkdir(parents=True)
        (snapshot/'id/SKILL.md').write_text('---\nname: team-rules\ndescription: fixture\n---\nTenant one rules\n')
        (snapshot/'.manifest.json').write_text(json.dumps({'tenant':'first','apiUrl':'https://example.invalid','skills':{'id':{}}}))
        (snapshot/'.synced-at').touch()
        m.sync(str(self.project))
        return m,creds,self.project/'.agents/skills/team-rules'

    def test_changed_tenant_cleanup_on_fresh_stop_and_failed_refresh(self):
        m,creds,target=self.tenant_fixture()
        self.assertTrue(target.exists())
        mirror=lambda project,wait=False:m.sync(str(project),wait=wait)
        creds.write_text(json.dumps({'altimateInstanceName':'second','altimateUrl':'https://example.invalid'}))
        with patch.object(refresh,'mirror',side_effect=mirror), patch.object(refresh,'project_directory',return_value=self.project), patch.object(sys,'argv',['refresh','--if-stale']), patch.dict(os.environ,self.env,clear=True), patch.object(refresh.subprocess,'Popen') as spawn:
            self.assertEqual(refresh.main(),0)
            spawn.assert_not_called()
        self.assertFalse(target.exists())
        creds.write_text(json.dumps({'altimateInstanceName':'first','altimateUrl':'https://example.invalid'}))
        m.sync(str(self.project));self.assertTrue(target.exists())
        creds.write_text(json.dumps({'altimateInstanceName':'second','altimateUrl':'https://example.invalid'}))
        with patch.object(refresh,'mirror',side_effect=mirror), patch.dict(os.environ,{**self.env,'REFRESH_TEST_FAIL':'1'},clear=True):
            self.assertEqual(refresh.refresh(self.project,wait=True),7)
        self.assertFalse(target.exists())

    def test_manual_refresh_does_not_claim_success_when_copy_busy(self):
        m,_,target=self.tenant_fixture()
        lock=self.project/'.altimate-code/codex-skill-copy.lock'
        with lock.open('w') as f, patch.object(m,'COPY_WAIT_SECONDS',.05), patch.object(refresh,'mirror',side_effect=lambda p,wait=False:m.sync(str(p),wait=wait)), patch.dict(os.environ,self.env,clear=True):
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(TimeoutError):
                refresh.refresh(self.project,wait=True)
            self.assertFalse(self.log.exists())
            self.assertTrue(target.exists())

    def test_post_refresh_copy_waits_for_concurrent_startup(self):
        m,_,_=self.tenant_fixture()
        with (self.project/'.altimate-code/codex-skill-copy.lock').open('w') as lock:
            def complete_refresh(*args,**kwargs):
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                return subprocess.CompletedProcess(args[0],0)
            with patch.object(m,'COPY_WAIT_SECONDS',.05), patch.object(refresh,'mirror',side_effect=lambda p,wait=False:m.sync(str(p),wait=wait)), patch.dict(os.environ,self.env,clear=True), patch.object(refresh.subprocess,'run',side_effect=complete_refresh):
                with self.assertRaises(TimeoutError):
                    refresh.refresh(self.project,wait=True)

    def test_removed_project_state_cleans_owned_copies(self):
        m,_,target=self.tenant_fixture()
        shutil.rmtree(self.project/'.altimate-code')
        with patch.object(refresh,'mirror',side_effect=lambda p,wait=False:m.sync(str(p),wait=wait)), patch.object(refresh,'project_directory',return_value=self.project), patch.object(sys,'argv',['refresh','--if-stale']), patch.dict(os.environ,self.env,clear=True), patch.object(refresh.subprocess,'Popen') as spawn:
            self.assertEqual(refresh.main(),0)
            spawn.assert_not_called()
        self.assertFalse(target.exists())


if __name__=='__main__':
    unittest.main()
