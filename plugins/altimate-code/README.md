# Altimate Code — Codex plugin

Routes dbt + warehouse tasks from Codex to [altimate-code](https://github.com/AltimateAI/altimate-code), a specialized open-source CLI agent with 100+ deterministic data-engineering tools: SQL anti-pattern detection, column-level lineage, dbt build/test/run against real warehouses, FinOps and cost analysis, cross-dialect translation and data parity, and PII detection.

**Why delegate?** General coding agents can edit SQL files; they can't inspect your live warehouse state. altimate-code gives Codex a deterministic data-engineering layer — indexed schemas, real query history, real cost data — instead of guesses.

## Install

```bash
# 1. Add the marketplace to your Codex
codex plugin marketplace add AltimateAI/altimate-codex-plugin

# 2. Open Codex, type /plugins, select "Altimate Code", install
codex
```

Adding the marketplace makes the plugin discoverable in the `/plugins` browser but does not install it — you install it explicitly from the browser, and Codex will prompt you to review and trust its SessionStart hook before it runs.

## Prerequisites

The altimate-code CLI must be installed and configured on your PATH:

```bash
npm install -g altimate-code     # requires Node 20+
altimate-code                    # launch the TUI, then run /connect to configure your LLM provider
```

Or configure a provider via environment variable (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and 20+ others — see the [altimate-code docs](https://docs.altimate.sh)).

If altimate-code is not on PATH or not configured, the plugin surfaces the failure with fix instructions rather than silently falling back to Codex's native tools.

## How it works

1. A **SessionStart hook** adds a static description of the plugin's two skills to the session, so Codex knows when a task fits. Codex prompts you to review and trust the hook the first time you start a session with the plugin installed; approve it once and it fires in every subsequent session.
2. **Delegation** — when a data-engineering task fires the **`altimate-code` skill** (or you invoke `/altimate-code:altimate <task>`), Codex runs `altimate-code run "<your task>"` locally, selecting the cheapest suitable agent persona (`fast-edit` for dbt/SQL edits, `analyst` for aggregation-heavy correctness work, `builder` for warehouse-state investigation).
3. **Review** — when the user asks to review dbt changes / PR / commit, the **`review` skill** (or `/altimate-code:review`) runs `altimate-code review` on the current dbt project and surfaces the signed verdict envelope verbatim (APPROVE / COMMENT / REQUEST_CHANGES).
4. altimate-code plans and executes each task using your configured LLM provider. Warehouse queries, dbt commands, and file edits run **locally under your credentials**.
5. The result is written to a private local temp file (delegation) or streamed to stdout (review) and surfaced back in your Codex conversation.

## Example prompts

Once installed, try these in Codex — the skills route them to altimate-code automatically. You can also invoke a skill explicitly with `/altimate-code:altimate <task>` or `/altimate-code:review [scope]`.

1. **Column-level lineage** — *"Trace the `revenue_usd` column in `models/marts/fct_revenue.sql` back to its sources, and list every downstream model that would be affected if I change its rounding."*
2. **Warehouse cost analysis** — *"Give me a cost report for our Snowflake account: the ten most expensive queries this month and any warehouses that look over-provisioned."*
3. **Cross-dialect validation** — *"Compare `prod.orders` in Snowflake with `analytics.orders` in BigQuery row-by-row using `id` as the key, and summarize any mismatches."*
4. **dbt test generation** — *"Generate dbt tests for `models/staging/stg_orders.sql`, including unit tests for the CASE/WHEN logic."*
5. **dbt PR review** — *"Review my dbt changes."* or *"Review PR #1158."* → the `review` skill produces a signed verdict envelope.

## Data handling

Delegating a task passes your prompt text to the altimate-code CLI, which sends it to your configured LLM provider — the Altimate LLM Gateway by default, or your own provider (BYOK), in which case Altimate never sees it. Warehouse credentials and query results stay on your machine.

Full details: **[PRIVACY.md](../../PRIVACY.md)** · Security policy and disclosure: **[SECURITY.md](../../SECURITY.md)** · Terms: **[TERMS.md](../../TERMS.md)**

## Troubleshooting

| Symptom | Fix |
|---|---|
| `command not found: altimate-code` | `npm install -g altimate-code` (Node 20+), then run `altimate-code` once to configure your provider. |
| `Unauthorized` / `No provider configured` | Run `altimate-code` to open the TUI and reconfigure your provider via `/connect`, or set the provider API key env var. |
| `Error: Unexpected error — Unknown: FileSystem.open (…altimate-code/log/opencode.log)` | Codex's default `workspace-write` sandbox blocks writes to `~/.local/share/altimate-code/log/`, where the CLI writes its log. Re-run with `codex exec --sandbox danger-full-access …`, or pass `-c 'sandbox_permissions=["disk-full-write-access"]'` on the specific invocation. Frequent users can raise the default in `~/.codex/config.toml`. Codex has no per-plugin sandbox-permission declaration in its manifest schema today, so this is a per-invocation flag. |
| Task hangs for several minutes | Open `altimate-code` to check for a pending prompt in the TUI, or re-run specifying a known-good model. |
| Empty result | The task may be too ambiguous — restate with the target table, expected columns, or time window. |
| `UNKNOWN_USER` / `Database does not exist` mid-run | The CLI connects but your warehouse credentials don't match this project — reconfigure warehouse auth in the `altimate-code` TUI or `profiles.yml`. |
| Plugin installed but never delegates | Confirm the SessionStart hook is trusted — Codex asks on first use; if you skipped it, uninstall and reinstall from `/plugins`. |
| Plugin doesn't appear in `/plugins` | Confirm the marketplace is registered: `codex plugin marketplace add AltimateAI/altimate-codex-plugin`, then re-open `/plugins`. |

Still stuck? See [Support](#support).

## Components

- **Skill** — `skills/altimate-code/SKILL.md` — delegation logic and agent-persona selection (byte-identical routing behavior with the Claude Code and opencode variants of this plugin, per the [agentskills.io](https://agentskills.io) open standard)
- **Skill** — `skills/review/SKILL.md` — dbt/SQL PR reviewer that runs `altimate-code review` and surfaces signed verdicts; declines non-dbt code review
- **Command** — `commands/altimate.md` — `/altimate-code:altimate <task>` explicit-delegation slash command with agent-persona selection
- **Command** — `commands/review.md` — `/altimate-code:review [scope]` explicit-review slash command; scope can be empty (working tree), a commit SHA, a branch name, or a GitHub PR URL / number
- **Hook** — `hooks/hooks.json` + `hooks/altimate-code-session-start.sh` — SessionStart capability description (static text only; no side effects)

## Support

- **Docs:** [docs.altimate.sh](https://docs.altimate.sh)
- **Issues:** [GitHub Issues](https://github.com/AltimateAI/altimate-codex-plugin/issues)
- **Community:** [Slack](https://altimate.studio/join-agentic-data-engineering-slack)
- **Email:** support@altimate.ai · security reports: security@altimate.ai

## License

MIT — see [LICENSE](../../LICENSE).
