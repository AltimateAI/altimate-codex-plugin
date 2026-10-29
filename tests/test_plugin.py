"""Exercise plugin entry points without changing account configuration or contacting data services."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

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



if __name__ == '__main__':
    unittest.main()
