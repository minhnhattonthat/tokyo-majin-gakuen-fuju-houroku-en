# Skill gotchas

- SKILL.md Step 0: the plugin's own guard hook did not block the canary in an Orca worker session; adding the `hooks` block (stable marketplace path) to `.claude/settings.json` took effect a few calls later in the same session without a reload.
- references/graphics.md §Survey: GBA card games store 8bpp art (all bytes < 0x80) beside 4bpp UI; a 4bpp-only vramfind misses it ("background codec" here was just 8bpp). Split assets at 4-aligned pointer targets; odd targets are struct fields.
- references/graphics.md §Survey: 8bpp tiles can also use only palette indices >= 0x80 (here 0x81-0x9F, card frames with a 0x140-byte palette); an "all bytes < 0x80" 8bpp test skips them as "records". Follow the pointer table to (tiles, palette, map) triples instead.
