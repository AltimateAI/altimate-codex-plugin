# Changelog

All notable changes to the Altimate Code Codex plugin are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-10-19

### Fixed
- The skills and slash commands now resolve the CLI as `altimate`, its canonical name since v0.7.1, and fall back to `altimate-code` for npm installs older than v0.7.1. Older curl and PowerShell installs expose only `altimate`, so the plugin previously reported "not installed" on machines where the CLI was present.
- Install guidance and recovery messages now list both the npm and curl install methods and point to `altimate` for first-run auth setup.
- The CLI lookup ignores aliases and shell functions, skips a non-executable `altimate` in favour of a working `altimate-code`, and runs before `gh pr checkout` in PR reviews, so a missing CLI never switches your branch. Recovery messages name `altimate-code` for npm installs older than v0.7.1.

## [1.0.0] — 2026-07-18

### Added
- Initial public release of the Codex variant.
- `altimate-code` skill — routes dbt / warehouse tasks to the [altimate-code](https://github.com/AltimateAI/altimate-code) CLI, with agent-persona selection (`fast-edit`, `analyst`, `builder`).
- `review` skill — runs `altimate-code review` on dbt project changes and surfaces the signed verdict envelope verbatim (APPROVE / COMMENT / REQUEST_CHANGES); read-only, declines non-dbt code review.
- `/altimate-code:altimate <task>` slash command for explicit delegation.
- `/altimate-code:review [scope]` slash command for explicit review; scope accepts empty, commit SHA, branch, or GitHub PR URL/number.
- SessionStart hook — publishes a fixed capability description of both skills so Codex can route between them.
- Marketplace metadata for install via `codex plugin marketplace add AltimateAI/altimate-codex-plugin`.

### Notes
- The skill routing behaviour is kept in parity with the Claude Code and opencode variants of this plugin, per the [agentskills.io](https://agentskills.io) open standard.
- Plugin ships opt-in: the marketplace makes it discoverable, but delegation only begins after the user explicitly installs it from Codex's `/plugins` browser and approves the SessionStart hook.
