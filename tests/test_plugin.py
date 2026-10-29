"""Exercise plugin entry points without changing account configuration or contacting data services."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/altimate-code'


class RoutingTests(unittest.TestCase):
    def startup(self, executable=False, mode=None, executable_name='altimate-code'):
        with tempfile.TemporaryDirectory(prefix='plugin mode ') as folder:
            folder = Path(folder)
            (folder / 'dirname').symlink_to(shutil.which('dirname'))
            marker = folder / 'executed'
            if executable:
                cli = folder / executable_name
                cli.write_text(f'#!/bin/sh\n: > "{marker}"\nexit 99\n')
                cli.chmod(0o755)
            env = dict(os.environ, PATH=str(folder))
            env.pop('ALTIMATE_DATA_MODE', None)
            if mode is not None:
                env['ALTIMATE_DATA_MODE'] = mode
            manifest = json.loads((PLUGIN / '.codex-plugin/plugin.json').read_text())
            hooks = json.loads((PLUGIN / manifest['hooks']).read_text())
            command = hooks['hooks']['SessionStart'][0]['hooks'][0]['command']
            env['PLUGIN_ROOT'] = str(PLUGIN)
            (folder / 'bash').symlink_to(shutil.which('bash'))
            result = subprocess.run(['/bin/sh', '-c', command], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists(), 'startup must never execute the data CLI')
            return result.stdout

    def test_missing_binary_and_altimate_only_emit_cli_hint(self):
        for available in (False, True):
            result = json.loads(self.startup(available, executable_name='altimate'))
            self.assertIn('CLI mode', result['hookSpecificOutput']['additionalContext'])

    def test_mcp_startup_is_silent(self):
        self.assertEqual(self.startup(True), '')

    def test_explicit_cli_and_invalid_override(self):
        self.assertIn('CLI mode', self.startup(True, 'cli'))
        self.assertEqual(self.startup(True, 'invalid'), '')
        self.assertIn('CLI mode', self.startup(False, 'mcp'))

    def test_native_shell_input_and_malformed_input(self):
        guard = PLUGIN / 'hooks/warehouse-guard.sh'
        env = dict(os.environ, ALTIMATE_ROUTE_GUARD='1')
        for key in ('command', 'cmd'):
            payload = json.dumps({'tool_name': 'exec_command', 'tool_input': {key: 'psql -c "select 1"'}})
            run = subprocess.run(['bash', str(guard)], input=payload, env=env, text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(run.stdout)['hookSpecificOutput']['permissionDecision'], 'deny')
        for payload in ('not json', '[]', '{"tool_input":null}', '{"tool_input":{"cmd":42}}'):
            run = subprocess.run(['bash', str(guard)], input=payload, env=env, text=True, capture_output=True, check=True)
            self.assertEqual(run.stdout, '')

    def test_manifest_wiring(self):
        marketplace = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        for entry in marketplace['plugins']:
            plugin = ROOT / entry['source']['path']
            manifest = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
            self.assertEqual(manifest['name'], entry['name'])
            self.assertTrue((plugin / manifest['skills']).is_dir())
            server = json.loads((plugin / manifest['mcpServers']).read_text())['mcpServers']['altimate-code']
            self.assertEqual(server['args'][:2], ['mcp', 'serve'])
            self.assertNotIn('CLAUDE', server['command'])
            self.assertTrue(all(len(x) <= 128 for x in manifest['interface']['defaultPrompt']))


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='codex package ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.core = self.root / 'core'
        self.core.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.core)], check=True)
        (self.core / 'source.ts').write_text('export const sentinel = 17\n')
        subprocess.run(['git', '-C', str(self.core), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.core), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture'], check=True)
        self.binary = self.root / 'altimate-code'
        self.binary.write_text('''#!/bin/sh
case "$*" in
  'mcp serve --help') echo '--workspace-tools' ;;
  'workspace-client --help') echo 'context remember engine-install' ;;
  '--version') echo 'fixture-runtime' ;;
  'mcp serve --workspace-tools') pwd ;;
  *) exit 81 ;;
esac
''')
        self.binary.chmod(0o755)
        self.stamp = self.root / 'build-inputs.json'
        self.stamp.write_text(json.dumps({'inputs': [{'path': 'source.ts', 'sha256': hashlib.sha256((self.core/'source.ts').read_bytes()).hexdigest()}], 'roots': ['.'], 'target': 'test-fixture', 'aggregate': 'fixture'}))
        self.output = self.root / 'pilot'

    def package(self):
        return subprocess.run([sys.executable, str(ROOT/'scripts/package-experimental.py'), '--binary', str(self.binary), '--core', str(self.core), '--output', str(self.output)], text=True, capture_output=True)

    def test_offline_package_and_existing_output(self):
        result = self.package()
        self.assertEqual(result.returncode, 0, result.stderr)
        marketplace = json.loads((self.output/'.agents/plugins/marketplace.json').read_text())
        plugin = self.output/marketplace['plugins'][0]['source']['path']
        manifest = json.loads((plugin/'.codex-plugin/plugin.json').read_text())
        server = json.loads((plugin/manifest['mcpServers']).read_text())['mcpServers']['altimate-code']
        binary = str(plugin / 'runtime/altimate-code')
        self.assertEqual(Path(binary).read_bytes(), self.binary.read_bytes())
        self.assertTrue(os.access(binary, os.X_OK))
        self.assertEqual(server['args'], ['./scripts/serve.sh'])
        self.assertIn('ALTIMATE_PROJECT_DIR', server['env_vars'])
        project = self.root / 'data project'
        project.mkdir()
        launch = subprocess.run([server['command'], *server['args']], cwd=plugin/server['cwd'], env=dict(os.environ, ALTIMATE_PROJECT_DIR=str(project)), text=True, capture_output=True)
        self.assertEqual(launch.returncode, 0, launch.stderr)
        self.assertEqual(Path(launch.stdout.strip()).resolve(), project.resolve())
        for value in ('', 'relative', str(self.root/'absent')):
            launch = subprocess.run([server['command'], *server['args']], cwd=plugin/server['cwd'], env=dict(os.environ, ALTIMATE_PROJECT_DIR=value), text=True, capture_output=True)
            self.assertEqual(launch.returncode, 2)
        with zipfile.ZipFile(self.output.with_suffix('.zip')) as archive:
            self.assertIn('pilot/.agents/plugins/marketplace.json', archive.namelist())
        self.assertNotEqual(self.package().returncode, 0)
        self.assertEqual(Path(binary).read_bytes(), self.binary.read_bytes())
        Path(binary).unlink()
        launch = subprocess.run([server['command'], *server['args']], cwd=plugin/server['cwd'], env=dict(os.environ, ALTIMATE_PROJECT_DIR=str(project)), text=True, capture_output=True)
        self.assertEqual(launch.returncode, 127)
        self.assertIn('runtime is missing', launch.stderr)

    def test_stale_and_added_source_rejected(self):
        original = (self.core/'source.ts').read_text()
        (self.core/'source.ts').write_text('changed')
        self.assertIn('stale', self.package().stderr)
        self.assertFalse(self.output.exists())
        (self.core/'source.ts').write_text(original)
        (self.core/'new.ts').write_text('new')
        self.assertIn('predates', self.package().stderr)
        self.assertFalse(self.output.exists())

    def test_wrong_runtime_and_existing_archive_rejected(self):
        self.binary.write_text('#!/bin/sh\necho unsupported\n')
        self.assertIn('does not support', self.package().stderr)
        self.assertFalse(self.output.exists())
        self.output.with_suffix('.zip').write_bytes(b'preserve')
        self.assertIn('archive already exists', self.package().stderr)
        self.assertEqual(self.output.with_suffix('.zip').read_bytes(), b'preserve')


if __name__ == '__main__':
    unittest.main()
