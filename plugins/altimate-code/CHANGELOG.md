# Changelog

All notable changes to the Altimate Code Codex plugin are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] — 2026-10-30

### Added
- Team rules from a linked Altimate workspace apply in Codex sessions. At session start the plugin gives Codex the workspace's approved rules for the repository, the number of proposed rules waiting for you, and the owner's reviews of your proposals since your last session.
- Corrections you make to Codex are recorded locally (UserPromptSubmit, no model call). After a turn, altimate-code checks them in the background (Stop) and keeps a proposed rule when you corrected the same topic in two sessions or corrected a team rule Codex was given.
- `/altimate-code:rules`: answer proposed rules (send for review, approve as owner, edit, save as memory, or "Not a rule"), and see the team rules and the review status of your proposals.
- The hooks run only in a linked project with learning on. They need an altimate-code release with `learn hook`; with an older one they do nothing.

## [1.1.0] — 2026-10-19

### Fixed
- The skills and slash commands now resolve the CLI as `altimate-code` and fall back to `altimate`. curl and PowerShell installs from v0.7.1 on may expose only `altimate`, so the plugin previously reported "not installed" on machines where the CLI was present. `altimate-code` is tried first because a different tool may own the generic `altimate` name.
- Install guidance and recovery messages now list both the npm and curl install methods and point to `altimate` for first-run auth setup.
- The CLI lookup ignores aliases and shell functions, skips a non-executable match in favour of the other name, and runs before `gh pr checkout` in PR reviews, so a missing CLI never switches your branch. Recovery messages name `altimate` for installs without `altimate-code`.

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
