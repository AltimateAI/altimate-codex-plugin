---
name: get-started
description: Set up the Altimate Code plugin, check the separately installed CLI, and explain optional lifecycle hooks for a manual Codex installation. Use when the user asks to set up Altimate or runs plugin setup.
---

# Get started with Altimate Code

Explain that the plugin supplies skills; the Altimate CLI is installed separately.
Setup runs when the user chooses it. Do not claim an automatic install-time banner.

1. Check for an executable `altimate-code`, then `altimate`, ignoring aliases and
   shell functions as in the other Altimate skills. Run the resolved executable
   with `--version` and confirm it identifies Altimate before using it. If a
   different program owns `altimate`, stop and explain the name conflict.
2. If absent, offer the documented installation choices:
   `npm install -g @altimateai/altimate-code` or
   `curl -fsSL https://www.altimate.sh/install | bash`.
   Explain the chosen command before installing; proceed only when the user
   asks to install. Never run both methods. Recheck the CLI afterward.
3. Ask the user to launch the resolved CLI in their terminal for interactive
   authentication and warehouse/workspace setup if needed. Never request tokens
   in chat. Do not launch an interactive TUI into a non-interactive tool call.
4. Explain the two included workflows: ask Altimate for dbt/warehouse help, or
   ask it to review dbt/SQL changes. Do not run a warehouse query or start a
   model-backed task merely to prove installation; let the user choose a task.

## Optional automatic session behavior

The directory package works without hooks. Offer this once during setup, not
every turn: the manual GitHub plugin adds session-start routing hints and, in
a linked workspace with the required CLI support, team rules. With learning
enabled, its prompt/Stop hooks can capture corrections and draft rule proposals.
These are optional. Explain the transcript processing and the Altimate CLI's
separate model/provider described in the repository's PRIVACY.md before enabling
learning; do not describe it as local-only processing.

If the user chooses the manual plugin, link to
https://github.com/AltimateAI/altimate-codex-plugin#install and guide them:

- Inspect existing installations in `/plugins`. Disable the directory copy
  before enabling the manual copy so skills and MCP servers are not duplicated.
- Add the marketplace with
  `codex plugin marketplace add AltimateAI/altimate-codex-plugin`, then select
  `altimate-code` in `/plugins` to install/enable it.
- Open `/hooks` in Codex CLI (or the desktop hook review UI) to inspect and trust
  the exact hook definitions. Never bypass trust or silently edit user config.
- Start a new session and confirm the hooks are listed and trusted. A successful
  package installation alone does not prove hook execution or workspace access.

If the installed Codex version lacks those controls, stop with its version and
link to the installation docs; do not invent a fallback installer. To undo the
optional installation, disable its hooks/plugin and re-enable the directory copy.
Do not promise remote MCP, skill refresh, or other capabilities unless present in
the installed plugin version.
