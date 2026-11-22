-- ppuat.lua: dump the PPU (VRAM, OAM, palette) once at a frame, for objsrc.py / bglayers.py.
--   emu.py ROM --out D --state-in S --route-str "..." --script tools/debug/ppuat.lua --var AT=100 [--var "OUTP='ppu'"]
-- OUTP is relative to the run's --out dir (writes D/ppu.vram.bin, .oam.bin, .pal.bin ...).
-- AT may be a table ({1970,2270}): one dump per frame, written as OUTP_<frame>.
local at, outp = AT or 100, OUTP or "ppu"
L.on_frame(function(n)
  if type(at) == "table" then
    for _, f in ipairs(at) do if n == f then L.dump_ppu(outp .. "_" .. f) end end
  elseif n == at then L.dump_ppu(outp) end
end)
