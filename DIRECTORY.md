# Altimate Code: directory installation

Altimate Code provides skills for dbt and warehouse work and dbt/SQL review.
The Altimate CLI must be installed separately. Run plugin setup (`get-started`)
to check the CLI, choose an installation method and configure authentication in
your terminal. Setup is user-initiated, not an automatic popup.

## Two distributions

| Capability | Public-directory ZIP | GitHub marketplace plugin |
|---|---|---|
| Altimate Code and review skills | Included, identical source files | Included |
| Guided setup skill and listing images | Included | Included |
| Lifecycle hooks and legacy commands | Excluded | Included |
| Local stdio MCP | Excluded by default; optional approved-partner build | Included when the source plugin provides it |
| Automatic team rules and optional learning | Not provided by this package | Requires trusted hooks, a linked workspace and a compatible CLI |

The GitHub plugin remains in `.codex-plugin/plugin.json` format. Do not add a
root Agent Plugins `plugin.json`: format changes can change hook loading.
The directory build derives a separate archive without modifying that source.

## Build from the repository

Run `python3 scripts/build_directory_zip.py`. The version comes from the source
manifest; the output is `dist/altimate-code-<version>.zip`. CI builds and uploads
this archive after its package tests pass. The archive root is the plugin root,
not a wrapping repository folder. Repeated builds of identical sources produce
identical bytes. Increase the source version for a new submission.

The builder includes only Markdown skills, image assets (with validated square
SVG listing icons), the legacy manifest,
this README and legal/security documents. It removes hooks, legacy commands,
app references and MCP registration, and sets `requires_local_executor: true`.
It rejects missing manifest-referenced icons and onboarding files, and unsupported
file types. It does not parse links or resource references inside skill Markdown;
check those manually during installation testing. New skills that require scripts need a deliberate
packaging change and tests before they can be included.

Only after OpenAI confirms local MCP eligibility for the submitting organization,
use `python3 scripts/build_directory_zip.py --include-local-mcp`. This requires a
source `.mcp.json` with stdio servers and creates a distinct `-local-mcp.zip`.
MCP `env` values must be `${VARIABLE}` references; literal values are rejected.
Machine-local paths in `command`, `args` (including `--option=path`) and `cwd`
are rejected. Use portable commands and review the entire configuration for secrets
before upload, including arguments and any additional fields. These checks are not
a general-purpose secret scanner.
The flag records the operator's choice; it cannot verify OpenAI allowlisting.
It does not add a server or bundle the separately installed CLI. Confirm that
external CLI dependency is accepted for your submission before uploading.

## Before submitting

The listing images use the existing Altimate gradient mark from
`AltimateAI/altimate-frontend`, `apps/web/src/assets/images/altimate_logo.svg`,
revision `854b86ad83d8d1a6cab576aab1dad1abfc573f78`.
The source SHA-256 is `d643aeef2a7ff3442901391f32b3f6bef280e9e8c7bcc164727030a0e93f6d1b`.
Only the outer SVG dimensions and viewBox differ: transparent square padding
centers the original artwork without changing its paths, gradients or colors.

- Complete organization/publisher identity verification and confirm submission
  access. A successful build is not directory approval.
- Test a clean desktop install, setup and the actual skills using the built ZIP.
- Select the listing route before the first upload: OpenAI currently does not
  support adding MCP to an existing skills-only listing. This builder does not
  implement a remote HTTPS MCP service.
- If skills-only submissions are rejected, reply to the review email or contact
  your OpenAI representative with the submission and organization IDs. Setting
  `requires_local_executor` does not bypass eligibility requirements.
- Recheck the [submission rules](https://developers.openai.com/plugins/deploy/submission)
  and [desktop-only rules](https://developers.openai.com/plugins/deploy/desktop-only).
  Desktop-only directory installation is documented for the ChatGPT desktop app;
  do not promise public-directory CLI installation.

## Optional hooks

For automatic session behavior, follow the
[GitHub installation instructions](https://github.com/AltimateAI/altimate-codex-plugin#install).
Disable the directory copy before enabling the manual plugin. Review and trust
hooks in `/hooks` in Codex CLI; new or changed definitions need review again.
Read [the privacy policy](https://github.com/AltimateAI/altimate-codex-plugin/blob/main/PRIVACY.md)
before enabling learning. To return to the directory version, disable the manual
plugin and re-enable the directory copy. The directory's core skills remain useful
without hooks; this optional flow must be disclosed during submission review.
