# altimate-codex-plugin

Altimate data engineering plugin for [Codex](https://developers.openai.com/codex/) — 11 skills covering dbt workflows, Snowflake query optimization, and delegation to the [`altimate-code`](https://github.com/AltimateAI/altimate-code) CLI agent.

> Same SKILL.md content shipping in the Claude Code [`data-engineering-skills`](https://github.com/AltimateAI/data-engineering-skills) plugin, the [`altimate-opencode-plugin`](https://github.com/AltimateAI/altimate-opencode-plugin), and the [`altimate-hermes-plugin`](https://github.com/AltimateAI/altimate-hermes-plugin) — the [agentskills.io](https://agentskills.io) open standard. This repo wraps them in the Codex plugin contract: a `.codex-plugin/plugin.json` manifest, a `.agents/plugins/marketplace.json` registry, and flat `skills/*` directories under one plugin root.

## What this gives your Codex agent

| Skill | What it does |
|---|---|
| `creating-dbt-models` | Creates dbt models following project conventions — discovers naming patterns first, runs `dbt build` to verify |
| `refactoring-dbt-models` | Safely refactors dbt models with downstream impact analysis |
| `debugging-dbt-errors` | Systematic dbt error debugging — reads the full error, checks upstream first, runs `dbt build` to verify |
| `testing-dbt-models` | Adds schema tests + data quality validation matching existing project patterns |
| `documenting-dbt-models` | Documents dbt models and columns in `schema.yml`, matching existing project style |
| `migrating-sql-to-dbt` | Converts legacy SQL (stored procs, views, ETL) into modular dbt models |
| `developing-incremental-models` | Develops and troubleshoots dbt incremental models — strategy / `unique_key` / partitioning |
| `finding-expensive-queries` | Finds and ranks expensive Snowflake queries by cost, time, or data scanned |
| `optimizing-query-by-id` | Optimizes Snowflake query performance using a `query_id` from `QUERY_HISTORY` |
| `optimizing-query-text` | Optimizes Snowflake SQL from provided query text — anti-pattern detection |
| `altimate-code` | Delegates multi-step data work to the `altimate-code` CLI agent (live warehouse access, column lineage, dbt builds, FinOps) |

All skills assume the agent has shell access to invoke `dbt`, `altimate-dbt`, and (for the `altimate-code` skill) the `altimate-code` CLI. They do **not** ship as MCP tools — the skill text instructs the agent on the right commands and conventions.

## Install

```bash
# 1. Add the marketplace to your Codex (clones the registry, makes the plugin findable)
codex plugin marketplace add AltimateAI/altimate-codex-plugin

# 2. Open Codex, type `/plugins`, select "Altimate Data Engineering", install
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

## Layout

```
altimate-codex-plugin/
├── .agents/plugins/
│   └── marketplace.json              # marketplace registry pointing at ./plugins/altimate
└── plugins/altimate/
    ├── .codex-plugin/
    │   └── plugin.json               # plugin manifest
    └── skills/
        ├── altimate-code/SKILL.md
        ├── creating-dbt-models/SKILL.md
        ├── debugging-dbt-errors/SKILL.md
        ├── developing-incremental-models/SKILL.md
        ├── documenting-dbt-models/SKILL.md
        ├── finding-expensive-queries/SKILL.md
        ├── migrating-sql-to-dbt/SKILL.md
        ├── optimizing-query-by-id/SKILL.md
        ├── optimizing-query-text/SKILL.md
        ├── refactoring-dbt-models/SKILL.md
        └── testing-dbt-models/SKILL.md
```

## Companion CLI

For the `altimate-code` delegation skill (and for `altimate-dbt` used in several other skills), install the companion CLI:

```bash
npm install -g altimate-code
```

This provides both the `altimate-code` agent and the `altimate-dbt` deterministic tool the dbt skills shell out to.

## License

MIT — see [LICENSE](./LICENSE).
