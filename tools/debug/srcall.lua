-- srcall.lua: log the first BIOS SWI (CpuSet / decompression) from each distinct ROM source r0: a map of every
-- graphic a run loads. Filter the log offline against the asset list (docs/re/graphics.md).
--   emu.py ... --script tools/debug/srcall.lua [--var SRC_MAX=4000]
-- Logs: SRCALL f<frame> lr r0 r1 r2
local max, n, seen = SRC_MAX or 4000, 0, {}
L.on_exec(0x00000008, 0x00000008, function()
  if n >= max then return end
  local s = emu.getState()
  local r0 = s["cpu.r0"]
  if r0 < 0x08000000 or r0 >= 0x0A000000 or seen[r0] then return end
  seen[r0] = true
  n = n + 1
  L.log(string.format("SRCALL f%d lr=%08X r0=%08X r1=%08X r2=%08X", L.frame, s["cpu.r14"], r0, s["cpu.r1"], s["cpu.r2"]))
end)
