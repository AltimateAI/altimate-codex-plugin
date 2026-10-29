# Altimate Code for Codex

Use Altimate MCP tools for warehouse SQL, lineage, PII, data diffs, FinOps, and dbt analysis. Codex supplies the reasoning. Plain file edits need no data tool.

See the [installation and mode guide](../../README.md). The manifest registers `.mcp.json` and `hooks/hooks.json` explicitly. SessionStart stays silent in the normal MCP path; a missing executable or `ALTIMATE_DATA_MODE=cli` adds CLI routing guidance. If Codex disables MCP or a server fails, the skill selects CLI using actual tool availability. No hook reads Claude settings or bypasses Codex policy.

CLI mode resolves `altimate-code`, falling back to `altimate`, then runs `tool context` once and `tool run <name> --workspace-tools --args '<json>' --json`. Use `tool schema <name> --workspace-tools` for unfamiliar arguments. A compatible companion build is required. Errors are reported, never replaced by invented results or ad-hoc database access.

Long multi-step jobs use explicit `run --agent builder`; dbt/SQL review uses the review skill. These operations may use a separately configured LLM. MCP and tool run do not launch a second reasoning agent; warehouse and workspace service costs still apply.

Set `ALTIMATE_ROUTE_GUARD=1` before starting Codex to enable the recognized-direct-query routing aid. It is disabled by default, fails open on parse errors, and is not a security control. Hooks require trust in Codex. Normal file operations, dbt compile/parse, and Altimate tool calls pass.

Try: “Compare row counts between prod and staging”, “Show column lineage for dim_customers”, or “Review my dbt changes”. Enable only this listing or the experimental listing at a time.

Workspace tools are enabled in both modes. Cached workspace skills are mirrored into `.agents/skills` at startup and after turns; stale snapshots refresh in the background at most once per hour after success. Use the refresh-skills skill for an immediate bounded refresh, or set `ALTIMATE_CODEX_SKILL_SYNC=0` to disable it. See the root guide for ownership, tenant checks and privacy.
