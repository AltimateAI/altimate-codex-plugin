---
name: refresh-skills
description: >-
  Refresh the linked Altimate workspace's skills into this project's Codex skills
  directory when the user asks for the latest team skills or conventions.
---

Run the plugin's `hooks/refresh-skills.sh --wait` with the shell working directory
set to the user's data project and stdin redirected from `/dev/null`.
Resolve the script relative to this SKILL.md: `../../hooks/refresh-skills.sh`.
Use the absolute resolved path; never assume PLUGIN_ROOT is present in ordinary
model shell calls. Show the outcome, including CLI or refresh failures.

Only workspace-owned copies in `.agents/skills` are replaced or removed. User
skills with the same name are preserved. `ALTIMATE_CODEX_SKILL_SYNC=0` disables
both background and manual sync. A manual refresh waits boundedly for any
in-flight refresh; it never steals its lock. No separately billed agent runs.

Codex detects project skill changes. If the current host does not show a newly
copied skill, start a new session; do not claim it loaded merely because it is
on disk. If not linked or signed in, follow the altimate-code workspace setup
instructions. Never publish skills or memory as part of refresh.
