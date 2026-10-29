#!/usr/bin/env bash
# Python owns locking, timeout and detached background execution.
command -v python3 >/dev/null 2>&1 || {
  if [ "${1:-}" = --wait ]; then printf '%s\n' 'python3 is required to refresh workspace skills.' >&2; exit 1; fi
  exit 0
}
exec python3 -I "$(dirname "$0")/refresh-workspace-skills.py" "${1:---if-stale}"
