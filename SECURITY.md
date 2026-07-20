# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in this plugin, please report it privately to **security@altimate.ai**. Do not open a public GitHub issue for security matters.

Include in your report:
- A description of the issue and its impact.
- Steps to reproduce.
- The plugin version (`plugins/altimate-code/.codex-plugin/plugin.json` → `version`) and, if relevant, the Codex version.

We will acknowledge receipt within 3 business days and aim to provide a status update within 10 business days.

## Data handling — what leaves your machine

This plugin's skill forwards the user's task text to the [altimate-code](https://github.com/AltimateAI/altimate-code) CLI, which then contacts the Altimate LLM gateway (or the user-configured provider) to plan and execute the work. Concretely:

- **User task prompt** → passed verbatim to `altimate-code run` → forwarded to Altimate's LLM gateway (or your BYOK provider).
- **Warehouse queries and dbt commands** → executed locally under your credentials by the CLI; not forwarded.
- **Query results and file edits** → produced locally; the CLI writes an output file which the plugin surfaces back to Codex.

If you do not want prompts to leave Codex's process, do not install this plugin. Adding the marketplace only makes it discoverable in Codex's `/plugins` browser — no delegation happens until you explicitly install it and approve the SessionStart hook.

For the complete privacy policy covering the plugin and the altimate-code CLI, see [PRIVACY.md](./PRIVACY.md).

## Supported versions

Only the latest published version receives security fixes.
