#!/usr/bin/env python3
"""Refresh workspace snapshots without waiting for network at session startup."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True

STALE_SECONDS = 3600
WAIT_SECONDS = 120
HERE = Path(__file__).resolve().parent


def project_directory():
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
            if isinstance(payload, dict) and isinstance(payload.get('cwd'), str):
                path = Path(payload['cwd'])
                if not path.is_absolute() or not path.is_dir():
                    raise ValueError('Invalid hook cwd')
                return path.resolve()
        except json.JSONDecodeError:
            pass
    return Path.cwd()


def mirror(project, wait=False):
    spec = importlib.util.spec_from_file_location('workspace_skill_mirror', HERE/'sync-workspace-skills.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.sync(str(project), wait=wait)


def eligible(project):
    state = project/'.altimate-code'
    return os.environ.get('ALTIMATE_CODEX_SKILL_SYNC') != '0' and state.is_dir() and not state.is_symlink()


def fresh(project):
    try:
        age = time.time() - (project/'.altimate-code/skill/_workspace/.synced-at').stat().st_mtime
        return 0 <= age < STALE_SECONDS
    except OSError:
        return False


def refresh(project, wait=False):
    if os.environ.get('ALTIMATE_CODEX_SKILL_SYNC') == '0':
        if wait:
            print('Workspace skill sync is disabled.')
        return 0
    # Also clear owned copies after all Altimate project state was removed.
    mirror(project, wait=True)
    if not eligible(project):
        if wait:
            print('Workspace skill sync is disabled or this project has no Altimate state.')
        return 0
    # Tenant cleanup is independent of CLI availability and network success.
    cli = shutil.which('altimate-code') or shutil.which('altimate')
    if not cli:
        if wait:
            print('altimate-code CLI not found (tried altimate-code, altimate).', file=sys.stderr)
        return 127 if wait else 0
    fd = os.open(project/'.altimate-code/codex-skill-refresh.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        deadline = time.monotonic() + (WAIT_SECONDS if wait else 0)
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if not wait:
                    return 0
                if time.monotonic() >= deadline:
                    print('Another workspace refresh is still running; try again later.', file=sys.stderr)
                    return 1
                time.sleep(0.1)
        if not wait and fresh(project):
            return 0
        for path in (project/'.agents', project/'.agents/skills'):
            if path.is_symlink():
                raise ValueError('Refusing a symlink destination')
            path.mkdir(exist_ok=True)
        try:
            result = subprocess.run([cli, 'workspace', 'refresh', '--directory', str(project)],
                                    cwd=project, stdin=subprocess.DEVNULL, timeout=WAIT_SECONDS)
        finally:
            # Refresh may change identity even when it fails. Never claim that
            # publication completed if another copy still owns the lock.
            mirror(project, wait=True)
        if result.returncode:
            return result.returncode
        if wait:
            count = sum(1 for p in (project/'.agents/skills').glob('*/.altimate-workspace-skill') if p.is_file() and not p.is_symlink())
            print(f'Workspace skills in .agents/skills: {count}.')
        return 0
    finally:
        os.close(fd)  # Kernel releases this lock even after a killed worker.


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--if-stale'
    if mode not in ('--if-stale', '--wait', '--startup', '--worker'):
        print('Expected --if-stale, --wait or --startup', file=sys.stderr)
        return 2
    project = Path(sys.argv[2]).resolve() if mode == '--worker' else project_directory()
    if mode in ('--wait', '--worker'):
        return refresh(project, wait=mode == '--wait')
    if os.environ.get('ALTIMATE_CODEX_SKILL_SYNC') == '0':
        return 0
    # Stop validates tenant identity even for a fresh snapshot.
    mirror(project)
    if not eligible(project):
        return 0
    if fresh(project):
        return 0
    subprocess.Popen([sys.executable, '-I', str(Path(__file__).resolve()), '--worker', str(project)],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        if '--wait' in sys.argv:
            print('Workspace skill refresh failed or timed out; existing skills were preserved.', file=sys.stderr)
            sys.exit(1)
        sys.exit(0)  # Advisory hooks must not break the user's turn.
