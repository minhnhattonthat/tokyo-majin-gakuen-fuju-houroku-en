-- ppuat.lua: dump the PPU (VRAM, OAM, palette) once at a frame, for objsrc.py / bglayers.py.
--   emu.py ROM --out D --state-in S --route-str "..." --script tools/debug/ppuat.lua --var AT=100 [--var "OUTP='ppu'"]
-- OUTP is relative to the run's --out dir (writes D/ppu.vram.bin, .oam.bin, .pal.bin ...).
local at, outp = AT or 100, OUTP or "ppu"
L.on_frame(function(n) if n == at then L.dump_ppu(outp) end end)
