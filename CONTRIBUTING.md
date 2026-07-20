# Contributing

Thanks for taking the time to contribute. This repo ships a single Codex plugin (`altimate-code`) that delegates data-engineering tasks to the [altimate-code](https://github.com/AltimateAI/altimate-code) CLI.

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
│       │   └── altimate-code/
│       │       └── SKILL.md                    # delegation logic
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

- **Routing behavior** (when Codex picks up the skill): edit `plugins/altimate-code/skills/altimate-code/SKILL.md` frontmatter description and/or `plugins/altimate-code/hooks/altimate-code-session-start.sh` `additionalContext`.
- **CLI invocation details** (agent selection, flags, follow-up handling): edit the workflow section in `plugins/altimate-code/skills/altimate-code/SKILL.md`.
- **Marketplace listing** (displayName, category, defaultPrompt): edit `plugins/altimate-code/.codex-plugin/plugin.json` `interface`.

## Cross-host parity

The skill body (`plugins/altimate-code/skills/altimate-code/SKILL.md`) is **byte-identical** to the same skill shipped in the Claude Code and opencode variants of this plugin, per the [agentskills.io](https://agentskills.io) open standard. If you change the skill body in this repo, you must land the same change in [`altimate-claude-plugin`](https://github.com/AltimateAI/altimate-claude-plugin) and [`altimate-opencode-plugin`](https://github.com/AltimateAI/altimate-opencode-plugin) in the same release — mismatch is a bug.

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

Smoke-install the plugin from your working copy:

```bash
# Register your local checkout as a marketplace source
codex plugin marketplace add ~/code/altimateai/altimate-codex-plugin

# Open Codex, install "Altimate Code" from /plugins, and approve the hook
codex
```

Then start a fresh Codex session in a dbt project and issue one of the sample prompts from [`plugins/altimate-code/README.md`](./plugins/altimate-code/README.md#example-prompts). You should see `altimate-code` invoked (a spinner from the CLI's TUI) rather than Codex trying to write dbt SQL directly.

To reset:

```bash
codex plugin marketplace remove altimate-codex-plugin
```

## Components

- **Skill** — `plugins/altimate-code/skills/altimate-code/SKILL.md` — the delegation logic (`altimate-code run "$USER_TASK"` and surface the result).
- **Hook** — `plugins/altimate-code/hooks/hooks.json` + `plugins/altimate-code/hooks/altimate-code-session-start.sh` — SessionStart hook that publishes a static capability description so Codex can route to the skill when the task shape fits.

## Reporting bugs / requesting features

Please open a GitHub issue on this repo. For security-sensitive reports, see [SECURITY.md](./SECURITY.md).
