# Contributing

Thanks for taking the time to contribute. This repo ships Codex data-tool plugins (`altimate-code` and an opt-in experimental listing) connected to the [altimate-code](https://github.com/AltimateAI/altimate-code) CLI.

## Quick start

1. Fork this repo and clone your fork.
2. Make your change in a topic branch off `main`.
3. Smoke-install the plugin locally (see [Testing changes](#testing-changes) below) and confirm Codex loads the marketplace, the plugin, the SessionStart hook, and the skill without errors.
4. Open a PR against `AltimateAI/altimate-codex-plugin:main`.

## Repo layout

```
altimate-codex-plugin/
├── .agents/plugins/
│   └── marketplace.json                        # marketplace registry pointing at ./plugins/altimate-code
├── plugins/
│   └── altimate-code/
│       ├── .codex-plugin/
│       │   └── plugin.json                     # plugin manifest
│       ├── skills/
│       │   ├── altimate-code/
│       │   │   └── SKILL.md                    # delegation logic
│       │   └── review/
│       │       └── SKILL.md                    # dbt/SQL PR reviewer routing
│       ├── commands/
│       │   ├── altimate.md                     # /altimate-code:altimate <task>
│       │   └── review.md                       # /altimate-code:review [scope]
│       ├── hooks/
│       │   ├── hooks.json                      # SessionStart hook definition
│       │   └── altimate-code-session-start.sh  # SessionStart hook script
│       ├── README.md                           # plugin-specific docs
│       └── CHANGELOG.md                        # plugin-specific changelog
├── README.md                                   # repo overview
├── PRIVACY.md
├── TERMS.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
└── LICENSE
```

## What to change where

- **Routing behavior** (when Codex picks up the delegation skill): edit `plugins/altimate-code/skills/altimate-code/SKILL.md` frontmatter description and/or `plugins/altimate-code/hooks/altimate-code-session-start.sh` `additionalContext`.
- **Review-skill routing** (when Codex picks up the review skill): edit `plugins/altimate-code/skills/review/SKILL.md` frontmatter description.
- **CLI invocation details** (agent selection, flags, follow-up handling): edit the workflow section in the relevant SKILL.md.
- **Slash-command bodies** (what `/altimate-code:altimate` and `/altimate-code:review` do when invoked explicitly): edit `plugins/altimate-code/commands/altimate.md` and `plugins/altimate-code/commands/review.md` respectively.
- **Marketplace listing** (displayName, category, defaultPrompt): edit `plugins/altimate-code/.codex-plugin/plugin.json` `interface`. Note the manifest schema's `defaultPrompt[*] <= 128` char ceiling — the marketplace rejects longer entries.

## Cross-host parity

Preserve data-tool behavior across the Claude, Codex and opencode variants. Host integration is intentionally different: Codex namespaces are discovered from session tools, hooks use PLUGIN_ROOT, and Codex owns MCP policy. Do not copy Claude settings detection or JavaScript UI mods into this package. Shared CLI resolver blocks remain identical within this repository.

Run `bash tests/resolve-cli.sh`, `bash tests/warehouse-guard.sh`, and `python3 -B -m unittest discover -s tests -p 'test_*.py'`. The Python tests drive hooks and build an offline experimental package using a deterministic fixture runtime; they do not establish live warehouse or workspace connectivity.

## Frontmatter — YAML gotcha

The `description:` field in `SKILL.md` is loaded as YAML frontmatter. If your description contains literal double quotes, wrap the value in a YAML folded block scalar (`>-`) so the parser doesn't trip on the embedded quotes and doesn't fold mid-token:

```yaml
---
name: altimate-code
description: >-
  Delegates ... "altimate" ...
---
```

`>-` (folded, strip) is preferred over `|` (literal): literal preserves internal newlines that Codex's manifest loader has historically rejected. Keep the description on one soft-wrapped line and let `>-` collapse whitespace on load.

## The manifest's `defaultPrompt` — 128-character ceiling

`plugin.json` → `interface.defaultPrompt[*]` entries are validated against a **128-character maximum** by `codex_core_plugins::manifest`. If you add a longer example the marketplace will reject the plugin at install time. Keep example prompts terse.

## Testing changes

If you touch the CLI resolver block in a skill or command, run `./tests/resolve-cli.sh` — it checks every copy is identical and resolves correctly in bash and zsh.

Smoke-install the plugin from your working copy:

```bash
# Register your local checkout as a marketplace source
codex plugin marketplace add ~/code/altimateai/altimate-codex-plugin

# Open Codex, install "Altimate Code" from /plugins, and approve the hook
codex
```

Then start a fresh Codex session in a dbt project and issue one of the sample prompts from [`plugins/altimate-code/README.md`](./plugins/altimate-code/README.md#example-prompts). Verify MCP tools are discovered and execute a read-only data question. Then disable MCP in Codex and verify model-free CLI fallback. Also test a missing CLI and a warehouse error; neither should trigger a second reasoning agent or invented data.

To reset:

```bash
codex plugin marketplace remove altimate-codex-plugin
```

## Components

- **Skill** — `plugins/altimate-code/skills/altimate-code/SKILL.md` — the delegation logic (`altimate-code run "$USER_TASK"` and surface the result).
- **Skill** — `plugins/altimate-code/skills/review/SKILL.md` — dbt/SQL PR reviewer routing (`altimate-code review` and present the signed verdict verbatim); declines non-dbt code review.
- **Command** — `plugins/altimate-code/commands/altimate.md` — `/altimate-code:altimate <task>` explicit-delegation slash command.
- **Command** — `plugins/altimate-code/commands/review.md` — `/altimate-code:review [scope]` explicit-review slash command.
- **Hook** — `plugins/altimate-code/hooks/hooks.json` + `plugins/altimate-code/hooks/altimate-code-session-start.sh` — SessionStart mode hint and opt-in direct-query guard. No hook starts a reasoning agent.

## Reporting bugs / requesting features

Please open a GitHub issue on this repo. For security-sensitive reports, see [SECURITY.md](./SECURITY.md).

## Workspace skill sync

The mirror writes only marked copies under the data project’s `.agents/skills`, never a provider profile. Tests inject fake Altimate metadata into the imported mirror module and leave HOME, CODEX_HOME, and inherited authentication untouched. Refresh tests use a local stub CLI and exercise fresh/stale timestamps, detached startup, lock contention, failed refresh and tenant changes. No tests invoke an LLM. Check startup and Stop wiring through Codex plugin/read; use skills/list to confirm generated project skills are recognized.
