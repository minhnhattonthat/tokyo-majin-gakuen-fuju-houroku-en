# Skill gotchas

- SKILL.md Step 0: the plugin's own guard hook did not block the canary in an Orca worker session; adding the `hooks` block (stable marketplace path) to `.claude/settings.json` took effect a few calls later in the same session without a reload.
