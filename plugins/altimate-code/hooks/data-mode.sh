#!/usr/bin/env bash
# Codex resolves layered/managed policy and exposes the resulting tools itself.
# Do not infer effective policy from Claude settings or a partial TOML layer.
altimate_data_mode() {
  case "${ALTIMATE_DATA_MODE:-}" in
    cli) printf 'cli\n'; return ;;
  esac
  local binary
  binary="$(unalias altimate-code 2>/dev/null; unset -f altimate-code 2>/dev/null; command -v altimate-code)"
  if [ -n "$binary" ] && [ -x "$binary" ]; then
    printf 'mcp\n'
  else
    printf 'cli\n'
  fi
}
