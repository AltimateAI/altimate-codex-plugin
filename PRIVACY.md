# Privacy policy

## Plugin and data flows

The plugin registers a local Altimate MCP server and supplies skills and shell hooks. Codex may start the server when the plugin is enabled. The normal server runs from PATH; the experimental package bundles a platform-specific runtime. Hooks emit mode guidance, inspect a proposed shell command for opt-in routing, or synchronize workspace skills.

Workspace skill synchronization reads the local workspace snapshot and Altimate sign-in tenant/API metadata to avoid serving another tenant's snapshot. It writes marked, sanitized skill copies under the project's `.agents/skills`. Startup and after-turn hooks may run `workspace refresh` in the background when the snapshot is absent or older than one hour, contacting the linked workspace through the companion CLI. No reasoning agent is launched and no memory publication is requested by these hooks. Set `ALTIMATE_CODEX_SKILL_SYNC=0` to disable this behavior. The companion CLI's telemetry configuration applies to refresh calls.

MCP and `tool run` execute data tools without a second reasoning agent. Results, schema metadata and workspace context returned to Codex enter the host model context and are subject to the host's data handling. Large results may be written to local spill files. Warehouse queries use configured connections and retain warehouse costs. Do not assume all returned data remains local.

Explicit `run` delegation and dbt review may send prompts and relevant data to the companion CLI's configured LLM provider. BYOK traffic follows that provider's policy. Workspace knowledge operations can use backend models and incur additional costs. Authentication and workspace operations communicate with Altimate services; credentials should be entered only through the runtime's supported authentication flow, never in chat.

The experimental skill forbids automatic memory publication. Publication requires an explicit user request and an available supported operation. Delegated jobs may persist local sessions and workspace memory according to companion CLI configuration. Delete sensitive output files after presenting delegated results.

Adding a marketplace does not enable its plugins. Install and enable the desired listing in Codex. Hook trust is separate from enabling the MCP server; skipping hook trust does not imply the MCP server is disabled. Disable the plugin or its MCP server in Codex to stop that integration.

## Usage telemetry

The altimate-code CLI emits anonymous product usage telemetry: event names, tool categories, token counts, timing, and error types. Telemetry never includes your code, queries, credentials, file paths, or prompt content, and error messages pass through a redaction layer (API keys, emails, and internal hostnames are masked). Events are keyed to an anonymous machine ID — a random UUID generated on first run and stored at `~/.altimate/machine-id`, not tied to your hardware or identity. For logged-in users, the email identifier is SHA-256 hashed before sending. The full event list is published in the [Telemetry reference](https://docs.altimate.sh/reference/telemetry/).

**Disabling telemetry:** set the environment variable `ALTIMATE_TELEMETRY_DISABLED=true`, or add the following to `~/.config/altimate-code/altimate-code.json`:

```json
{ "telemetry": { "disabled": true } }
```

**Retention:** telemetry is sent to Azure Application Insights and retained according to Microsoft's data retention policies; we do not maintain a separate telemetry data store. To request deletion of your telemetry data, contact **privacy@altimate.ai**.

## Third parties

- **LLM providers** — the provider you configure processes your prompts under its own terms and privacy policy. The default Altimate LLM Gateway is operated by Altimate; see the [Security FAQ](https://docs.myaltimate.com/arch/faq/) for its data handling.
- **Cloud infrastructure** — Altimate services and telemetry run on major cloud providers with encryption in transit (TLS) and at rest.
- **OpenAI** — your use of Codex itself is governed by OpenAI's terms and privacy policy, independent of this plugin.

We do not sell your data, and we do not use your data to train models.

## Security

All data transmitted to Altimate services is encrypted in transit using TLS. Altimate AI is SOC 2 Type 2 certified. To report a vulnerability, email **security@altimate.ai** (see [SECURITY.md](./SECURITY.md)).

## Your choices

- **Don't install the plugin** — adding the marketplace makes it discoverable but does not install it; the integration is enabled only after you install and enable a listing in Codex. Hook trust controls hooks separately.
- **Use BYOK** — route prompts directly to your own provider so Altimate never sees them.
- **Disable telemetry** — see above.
- **Contact us** — for access, correction, or deletion requests, email **info@altimate.ai**.

## Children

The plugin and the altimate-code CLI are professional developer tools, not directed at children, and not intended for use by anyone under 18.

## Changes to this policy

We will update this document in this repository and revise the effective date when our practices change. Material changes to Altimate-wide practices are governed by the master [Privacy Policy](https://www.altimate.ai/privacy).

## Contact

Altimate Inc. · 440 North Wolfe Road #150, Sunnyvale, CA 94085, USA · +1 (650) 254-6266
Privacy & general: **info@altimate.ai** · Security: **security@altimate.ai** · Support: **support@altimate.ai**
