#!/usr/bin/env bash
# Legacy Codex MCP resolves cwd relative to the plugin but not command variables.
# Bind an explicit project so workspace reads never silently use the plugin folder.
set -eu
PLUGIN_DIRECTORY="$(cd -- "$(dirname -- "$0")/.." && pwd)"
case "${ALTIMATE_PROJECT_DIR:-}" in
  /*) ;;
  *) printf '%s\n' 'Set ALTIMATE_PROJECT_DIR to the absolute data-project directory before starting Codex.' >&2; exit 2 ;;
esac
if [ ! -d "$ALTIMATE_PROJECT_DIR" ]; then
  printf '%s\n' 'ALTIMATE_PROJECT_DIR is not a directory.' >&2
  exit 2
fi
if [ ! -x "$PLUGIN_DIRECTORY/runtime/altimate-code" ]; then
  printf '%s\n' 'The experimental runtime is missing. Install a verified bundled package.' >&2
  exit 127
fi
cd -- "$ALTIMATE_PROJECT_DIR"
exec "$PLUGIN_DIRECTORY/runtime/altimate-code" mcp serve --workspace-tools
