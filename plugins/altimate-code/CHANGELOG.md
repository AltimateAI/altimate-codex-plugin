# Changelog

All notable changes to the Altimate Code Codex plugin are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-07-18

### Added
- Initial public release of the Codex variant.
- `altimate-code` skill — routes dbt / warehouse tasks to the [altimate-code](https://github.com/AltimateAI/altimate-code) CLI, with agent-persona selection (`fast-edit`, `analyst`, `builder`).
- SessionStart hook — publishes a fixed capability description so Codex can route to the skill.
- Marketplace metadata for install via `codex plugin marketplace add AltimateAI/altimate-codex-plugin`.

### Notes
- The skill body is byte-identical to the Claude Code and opencode variants of this plugin, per the [agentskills.io](https://agentskills.io) open standard.
- Plugin ships opt-in: the marketplace makes it discoverable, but delegation only begins after the user explicitly installs it from Codex's `/plugins` browser and approves the SessionStart hook.
