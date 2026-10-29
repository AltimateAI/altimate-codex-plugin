# altimate-codex-plugin

Codex plugin for [altimate-code](https://github.com/AltimateAI/altimate-code) data tools: warehouse SQL, column lineage, PII, data diffs, dbt, and FinOps.

## What this gives your Codex agent

- **MCP first:** the plugin starts `altimate-code mcp serve --workspace-tools`; Codex calls its tools directly and supplies the reasoning.
- **Model-free CLI fallback:** when tools are unavailable, resolve `altimate-code` or `altimate`, run `tool context` once, then `tool run`. This requires a companion build supporting those commands. Missing commands are reported; no automatic install or second agent fallback occurs.
- **Read-only analyst skill:** schema/value checks and database-computed answers, adapted from the companion analyst persona.
- **Explicit delegation and review:** long multi-step jobs use the builder agent; the review skill handles dbt/SQL changes and declines unrelated application code.
- **Opt-in warehouse guard:** `ALTIMATE_ROUTE_GUARD=1` redirects recognized direct query commands toward Altimate tools. It is a routing aid, not a security boundary or complete shell parser. Python 3 or jq is needed to parse hook input; missing parsers or malformed input fail open.

The SessionStart hook adds a CLI hint when the MCP executable is missing or `ALTIMATE_DATA_MODE=cli`; otherwise routing stays silent. Actual session tool availability determines fallback when Codex policy disables MCP or the server fails. `ALTIMATE_DATA_MODE=mcp` cannot override policy or make a missing executable available. CLI fallback still obeys Codex permissions.

## Workspace skills and refresh

The normal MCP server now enables `--workspace-tools`. Both MCP and CLI mode use workspace_context, workspace_skill and workspace_execute for linked team knowledge and read-only workspace warehouse operations. CLI tool run/list/schema calls include `--workspace-tools`; linking disables automatic memory upload. Publishing skills or memory remains an explicit user action.

At startup, cached workspace skills are mirrored into the data project's `.agents/skills`, then stale snapshots are refreshed in the background. A Stop hook checks again after turns, refreshing snapshots older than an hour. There is no timer while Codex is idle and no network wait before the first prompt. Use the **refresh-skills** skill to refresh immediately and see the outcome. Set `ALTIMATE_CODEX_SKILL_SYNC=0` to disable all mirroring and refresh.

Mirroring checks the snapshot tenant and API URL against local Altimate sign-in metadata. Only marked workspace copies are replaced or removed; same-name user skills survive. Active frontmatter, nested host configuration and symlinks are excluded. Copied skills remain workspace-authored guidance, never authority to override the user. Background failures preserve the cached snapshot; manual refresh reports failures. Codex discovers `.agents/skills`; if a host version does not reload a newly copied skill, start a fresh session.

The separately packaged [experimental listing](plugins/altimate-code-experimental/README.md) adds workspace tools with a verified bundled runtime. Enable only one listing. It is omitted from the source marketplace because its runtime is absent until packaging. Claude-specific setup dialogs and SQL panes are not available in Codex; setup requirements and results appear in chat.

## Install

```bash
# 1. Add the marketplace to your Codex
codex plugin marketplace add AltimateAI/altimate-codex-plugin

# 2. Open Codex, type `/plugins`, select "Altimate Code", install
codex
```

You can also add a local clone or a different git ref:

```bash
codex plugin marketplace add ~/code/altimateai/altimate-codex-plugin       # local path
codex plugin marketplace add AltimateAI/altimate-codex-plugin --ref main   # pinned ref
```

To refresh:

```bash
codex plugin marketplace upgrade altimate-codex-plugin
```

To remove the marketplace registration:

```bash
codex plugin marketplace remove altimate-codex-plugin
```

### Trusting hooks

Codex requires review and trust of plugin hook definitions before running them. Trust the current definition through Codex; edits may require renewed trust. The skills and MCP tools do not require the routing hook. Lifecycle hooks are intended for manual/local Codex installations, not public directory submission.

## Layout

```
altimate-codex-plugin/
├── .agents/plugins/
│   └── marketplace.json                        # marketplace registry pointing at ./plugins/altimate-code
└── plugins/altimate-code/
    ├── .codex-plugin/
    │   └── plugin.json                         # plugin manifest
    ├── hooks/
    │   ├── hooks.json                          # SessionStart and opt-in PreToolUse hooks
    │   └── altimate-code-session-start.sh      # hook script (routing hint)
    ├── commands/
    │   ├── altimate.md                         # /altimate-code:altimate
    │   └── review.md                           # /altimate-code:review
    └── skills/
        ├── altimate-code/SKILL.md              # delegation skill
        └── review/SKILL.md                     # dbt change review skill
```

## Companion CLI

MCP mode needs `altimate-code` on PATH; CLI fallback also accepts `altimate`. Install the companion CLI:

```bash
npm install -g altimate-code                       # Node 20+; exposes `altimate` and `altimate-code`
curl -fsSL https://www.altimate.sh/install | bash  # standalone binary; exposes `altimate`
```

After install, run `altimate` once to configure your LLM provider auth and warehouse connections through the TUI.

## License & legal

- **License:** MIT — see [LICENSE](./LICENSE).
- **Privacy:** [PRIVACY.md](./PRIVACY.md) — what the plugin collects, what it doesn't, and where prompts go.
- **Terms of use:** [TERMS.md](./TERMS.md) — governs your use of the plugin and the connected Altimate services.
- **Security disclosure:** [SECURITY.md](./SECURITY.md) — how to report a vulnerability.
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md) · [Code of Conduct](./CODE_OF_CONDUCT.md).
