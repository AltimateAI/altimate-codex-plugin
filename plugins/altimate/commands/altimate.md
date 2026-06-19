# /altimate

Delegate a task to altimate-code, the specialised data-engineering CLI agent. Use for live warehouse access, column-level lineage, downstream-impact analysis, cross-database migration / parity / validation, FinOps cost attribution, schema diff, PII detection from sampled rows, query optimization with real profile data, or anything that requires inspecting actual warehouse state.

Do NOT use this command for pure file/code edits to dbt models or SQL — codex with native tools is faster and accurate for those, and altimate-code's discovery loop is overkill.

## Arguments

- `<task description>` (required): the natural-language task to delegate. Pass it verbatim — do not paraphrase or split it.

## Workflow

You MUST run the task via the `altimate-code` CLI. Do NOT attempt the work with native tools (`bash`, `apply_patch`, `update_plan`, file edits).

1. Verify altimate-code is installed:
   ```
   command -v altimate-code
   ```
   If it returns nothing, stop and tell the user:
   > altimate-code is not installed. Install with `npm install -g altimate-code` (Node 20+), then run `altimate-code` once to configure your provider/warehouse auth, then re-run `/altimate <task>`.

2. Run altimate-code with the user's task:
   ```
   altimate-code run "<task>" \
     --yolo \
     --output /tmp/altimate-result.md \
     --dir "$(pwd)"
   ```

3. Read `/tmp/altimate-result.md` and present its contents to the user verbatim — no re-summarising, no re-formatting, no commentary. altimate-code has already produced the answer.

## Escalation

On any altimate-code error (`Unauthorized: Incorrect auth token`, `Token limit reached`, `No provider configured`, warehouse credential mismatch, process timeout):

- Surface the error message to the user along with the fix from the SKILL.md failure-modes table (`reconfigure auth via altimate-code TUI`, `add credits at https://<instance>.app.myaltimate.com/settings/credits`, `restate the prompt with more detail`, etc.).
- Do NOT fall back to native tools. The user invoked `/altimate` specifically to use altimate-code; falling back would defeat the purpose.
