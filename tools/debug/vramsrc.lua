-- vramsrc.lua: who writes non-zero data into a VRAM (or any) range, with registers, to find a graphic's source.
--   warp.py ROW --script tools/debug/vramsrc.lua --var WATCH_LO=0x0600D220 [--var WATCH_HI=..] [--var FROM=1600]
-- Logs up to SRC_MAX (40) lines: VSRC f<frame> pc lr r0-r3 addr value. A BIOS pc (< 0x4000) means CpuSet /
-- decompression: r0 is then the source (if the call is still in progress the registers hold its loop state).
local lo = assert(WATCH_LO, "set --var WATCH_LO=0x...")
local hi, from, max = WATCH_HI or lo + 31, FROM or 0, SRC_MAX or 40
local n = 0
L.on_write(lo, hi, function(addr, value)
  if L.frame < from or n >= max or value == 0 then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("VSRC f%d pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X addr=%08X v=%X", L.frame,
    L.pc(), s["cpu.r14"], s["cpu.r0"], s["cpu.r1"], s["cpu.r2"], s["cpu.r3"], addr, value))
end)
