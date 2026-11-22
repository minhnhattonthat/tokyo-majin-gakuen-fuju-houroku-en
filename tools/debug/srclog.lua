-- srclog.lua: log each BIOS SWI (CpuSet / decompression) whose source r0 lies in a ROM range: when a graphic loads.
--   emu.py ... --script tools/debug/srclog.lua --var SRC_LO=0x08ACCCCC --var SRC_HI=0x08B56000 [--var SRC_MAX=200]
-- Logs: SRC f<frame> lr r0 r1 r2 (once per distinct r0 and frame).
local lo = assert(SRC_LO, "set --var SRC_LO=0x...")
local hi, max, n, last = SRC_HI or lo + 0x1000, SRC_MAX or 200, 0, {}
L.on_exec(0x00000008, 0x00000008, function()
  if n >= max then return end
  local s = emu.getState()
  local r0 = s["cpu.r0"]
  if r0 < lo or r0 >= hi or last[r0] == L.frame then return end
  last[r0] = L.frame
  n = n + 1
  L.log(string.format("SRC f%d lr=%08X r0=%08X r1=%08X r2=%08X", L.frame, s["cpu.r14"], r0, s["cpu.r1"], s["cpu.r2"]))
end)
