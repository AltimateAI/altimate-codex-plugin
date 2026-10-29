#!/usr/bin/env bash
# Startup is a hint only. Actual session tools determine MCP availability.
# Mirror cached skills locally; stale refresh is detached and bounded.
# Never override Codex MCP policy or start a reasoning agent here.
if command -v python3 >/dev/null 2>&1; then
  bash "$(dirname "$0")/refresh-skills.sh" --startup >/dev/null 2>&1
fi
. "$(dirname "$0")/data-mode.sh"
if [ "$(altimate_data_mode)" = cli ]; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Altimate CLI mode: use the altimate-code skill for warehouse data, lineage, PII, data diffs and FinOps. Resolve altimate-code (falling back to altimate), run tool context once, then tool run <tool> --workspace-tools --args <json> --json. These calls run no second reasoning agent. Use tool schema --workspace-tools for exact arguments. Workspace questions start with workspace_context; use workspace_skill and workspace_execute with the returned token and schemas. Tokens belong on stdin, never in command arguments. Report failures; do not bypass them with direct database clients. Plain code edits use normal tools. Explicit long jobs may use run; dbt review uses the review skill. Honor Codex permissions and the user scope."}}'
fi
