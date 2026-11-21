# Reverse-engineering notes

One file per subsystem. Mark every finding **verified** (and how) or **guess** (and why). Addresses are for the dump
in `rom.sha1`.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | encoding, control codes, text regions, pointer tables, story scene format, free space, compression | encoding and tables verified; opcode set and font partly guessed |
| [graphics.md](graphics.md) | tile-drawn Japanese survey | tour part done; static sweep and mid-game screens open |
