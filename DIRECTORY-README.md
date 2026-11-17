# Altimate Code

This desktop plugin provides skills for dbt and warehouse work and dbt/SQL review.
Choose plugin setup or ask “Set up Altimate” to get started. Setup is user initiated.

The Altimate CLI is installed separately. Setup checks for `altimate-code` or
`altimate`, explains installation choices, and guides you to authenticate in your
own terminal. You can request the npm installation:

```sh
npm install -g @altimateai/altimate-code
```

For the standalone installer, follow the
[CLI installation instructions](https://github.com/AltimateAI/altimate-code)
in your own terminal. Then choose a dbt/warehouse task or request a dbt/SQL review.

This directory package excludes lifecycle hooks. For optional automatic session
behavior and workspace team rules, follow the
[full GitHub plugin installation](https://github.com/AltimateAI/altimate-codex-plugin#install).
Disable the directory copy first to avoid duplicate skills. Review and trust the
manual plugin's hooks before use. This is a guided switch, not an automatic upgrade.
To switch back, disable the manual copy and re-enable the directory copy.

Read [PRIVACY.md](PRIVACY.md) before enabling learning. The CLI and its provider
have separate authentication and data processing. See [TERMS.md](TERMS.md) and
[SECURITY.md](SECURITY.md), or [get support](https://github.com/AltimateAI/altimate-codex-plugin/issues).
