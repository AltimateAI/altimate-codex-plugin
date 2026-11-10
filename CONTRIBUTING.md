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
│       │   ├── altimate-code/
│       │   │   └── SKILL.md                    # delegation logic
│       │   └── review/
│       │       └── SKILL.md                    # dbt/SQL PR reviewer routing
│       ├── commands/
│       │   ├── altimate.md                     # /altimate-code:altimate <task>
│       │   ├── review.md                       # /altimate-code:review [scope]
│       │   └── rules.md                        # /altimate-code:rules
│       ├── hooks/
│       │   ├── hooks.json                      # SessionStart, UserPromptSubmit and Stop hook definitions
│       │   ├── altimate-code-session-start.sh  # SessionStart capability description
│       │   └── altimate-code-workspace-rules.sh # team rules hooks (session-start, user-prompt-submit, stop)
│       ├── README.md                           # plugin-specific docs
│       └── CHANGELOG.md                        # plugin-specific changelog
├── .github/workflows/
│   └── tests.yml                               # runs tests/*.sh on Linux and macOS
├── tests/
│   ├── resolve-cli.sh                          # CLI resolver block check
│   └── workspace-rules-hook.sh                 # workspace-rules hook check
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

Run the shell tests before opening a PR (CI runs them too, on Linux and macOS):

```bash
bash tests/resolve-cli.sh          # the CLI resolver block: every copy identical, resolves in bash and zsh
bash tests/workspace-rules-hook.sh # the workspace-rules hook against a stub CLI (needs python3 and git)
```

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
- **Skill** — `plugins/altimate-code/skills/review/SKILL.md` — dbt/SQL PR reviewer routing (`altimate-code review` and present the signed verdict verbatim); declines non-dbt code review.
- **Command** — `plugins/altimate-code/commands/altimate.md` — `/altimate-code:altimate <task>` explicit-delegation slash command.
- **Command** — `plugins/altimate-code/commands/review.md` — `/altimate-code:review [scope]` explicit-review slash command.
- **Hook** — `plugins/altimate-code/hooks/hooks.json` + `plugins/altimate-code/hooks/altimate-code-session-start.sh` — SessionStart hook that publishes a static capability description of both skills so Codex can route between them when the task shape fits.
- **Command** — `plugins/altimate-code/commands/rules.md` — `/altimate-code:rules` to answer proposed team rules.
- **Hooks** — `plugins/altimate-code/hooks/altimate-code-workspace-rules.sh` — the team rules hooks (SessionStart, UserPromptSubmit, Stop), which call `altimate-code learn hook <event>` only in a folder altimate-code's link cache names, and never fail the session.

## Reporting bugs / requesting features

Please open a GitHub issue on this repo. For security-sensitive reports, see [SECURITY.md](./SECURITY.md).
