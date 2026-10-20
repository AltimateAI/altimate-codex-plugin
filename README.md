# altimate-codex-plugin

Codex plugin that delegates dbt and warehouse work to [`altimate-code`](https://github.com/AltimateAI/altimate-code) — a specialised CLI agent for column-level lineage, dbt build/test/run, warehouse profiling, FinOps reporting, cross-database validation, and connectivity to Snowflake / BigQuery / Redshift / Databricks / Postgres / MySQL / DuckDB.

## What this gives your Codex agent

Two skills and matching slash commands. **`altimate-code`** routes tasks that touch live warehouse state, column lineage, cross-database work, query-cost attribution, schema diffs, PII detection, or FinOps reporting to the altimate-code subprocess. The skill body encodes:

- how to resolve the CLI (`altimate-code`, falling back to `altimate`) and detect that it is not installed
- which agent persona (`fast-edit` / `analyst` / `builder`) to pick for the task shape
- the exact non-interactive invocation with `--yolo` / `--output` / `--dir`
- when to add `--continue` for follow-up tasks in a warm session
- how to surface each failure mode to the user

**`review`** runs `altimate-code review` on dbt project changes (a local diff or a PR) and reports the findings. The slash commands `/altimate-code:altimate` and `/altimate-code:review` invoke the same flows explicitly.

The plugin also ships a `SessionStart` hook that emits a short routing hint into Codex's context so the model prefers delegation over reimplementing warehouse workflows with native tools.

## Install

```bash
# 1. Add the marketplace to your Codex
codex plugin marketplace add AltimateAI/altimate-codex-plugin

# 2. Open Codex, type `/plugins`, select "Altimate Code", install
codex
```

You can also add a local clone or a different git ref:

```bash
codex plugin marketplace add ~/code/altimateai/altimate-codex-plugin       # local path
codex plugin marketplace add AltimateAI/altimate-codex-plugin --ref main   # pinned ref
```

To refresh:

```bash
codex plugin marketplace upgrade altimate-codex-plugin
```

To remove the marketplace registration:

```bash
codex plugin marketplace remove altimate-codex-plugin
```

### Trusting the SessionStart hook

The plugin ships a `SessionStart` hook that injects a short routing hint into the model's context so it prefers the `altimate-code` skill for warehouse-touching work. Codex does not run plugin-bundled hooks automatically — the first time you start a session with the plugin installed, Codex will prompt you to review and trust the hook definition. Approve it once and the hook fires in every subsequent session; skip it and the plugin still installs but the routing hint won't be delivered.

## Layout

```
altimate-codex-plugin/
├── .agents/plugins/
│   └── marketplace.json                        # marketplace registry pointing at ./plugins/altimate-code
└── plugins/altimate-code/
    ├── .codex-plugin/
    │   └── plugin.json                         # plugin manifest
    ├── hooks/
    │   ├── hooks.json                          # SessionStart hook definition
    │   └── altimate-code-session-start.sh      # hook script (routing hint)
    ├── commands/
    │   ├── altimate.md                         # /altimate-code:altimate
    │   └── review.md                           # /altimate-code:review
    └── skills/
        ├── altimate-code/SKILL.md              # delegation skill
        └── review/SKILL.md                     # dbt change review skill
```

## Companion CLI

The delegation skill spawns `altimate-code` as a subprocess. Install the companion CLI:

```bash
npm install -g altimate-code                       # Node 20+; exposes `altimate` and `altimate-code`
curl -fsSL https://www.altimate.sh/install | bash  # standalone binary; exposes `altimate`
```

After install, run `altimate` once to configure your LLM provider auth and warehouse connections through the TUI.

## License & legal

- **License:** MIT — see [LICENSE](./LICENSE).
- **Privacy:** [PRIVACY.md](./PRIVACY.md) — what the plugin collects, what it doesn't, and where prompts go.
- **Terms of use:** [TERMS.md](./TERMS.md) — governs your use of the plugin and the connected Altimate services.
- **Security disclosure:** [SECURITY.md](./SECURITY.md) — how to report a vulnerability.
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md) · [Code of Conduct](./CODE_OF_CONDUCT.md).
