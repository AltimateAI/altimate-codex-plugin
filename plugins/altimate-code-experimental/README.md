# Altimate Code Experimental for Codex

This opt-in listing uses workspace context and native MCP tools without a second reasoning agent. Enable only one Altimate listing at a time.

This plugin is omitted from the source marketplace; the generated offline marketplace includes it. Installation requires a matching bundled runtime before installation. Build an offline package with `python3 scripts/package-experimental.py --binary /path/to/altimate-code --core /path/to/altimate-code-source --output /new/pilot-directory`. Python 3.9+ is required. The binary must have its adjacent `build-inputs.json` and support `mcp serve --workspace-tools` and `workspace-client`. The packager verifies source stamps, preserves existing outputs, and records provenance; it never downloads a runtime.

Register the generated directory as a Codex local marketplace. The package is platform-specific; Windows packaging is unavailable.

Start Codex from the data project with `ALTIMATE_PROJECT_DIR="$PWD" codex`. For desktop use, set that absolute project path in the environment inherited by Codex before launching it. The bundled launcher requires this explicit binding: Codex resolves the legacy MCP `cwd` to the plugin directory, while Altimate needs the data-project directory for workspace context. Missing, relative or nonexistent paths fail before starting the runtime. Restart the MCP server with a new binding when changing projects. The launcher preserves all account settings and never installs or downloads a runtime.

Ask local SQL questions directly. For company conventions and knowledge, Codex reads workspace_context and uses the returned operation schemas. Local data does not require Altimate sign-in. Workspace setup requirements are reported in chat; complete setup with the matching runtime and ask Codex to refresh context. Credentials never belong in chat.

Claude-specific setup dialogs, automatic question resumption, SQL result panes and inspector commands are not provided. Results appear in chat. Cancellation or a new question must never resume previous work. Memory publication is explicit only; workspace knowledge may incur backend model costs, and queries retain warehouse costs.
