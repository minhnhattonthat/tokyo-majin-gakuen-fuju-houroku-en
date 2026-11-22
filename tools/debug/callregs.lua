-- callregs.lua: log registers each time a function is entered (to find a callee's callers and arguments).
--   emu.py ... --script tools/debug/callregs.lua --var CALL_AT=0x080640F4 [--var FROM=0] [--var CALL_MAX=40]
-- Logs: CALL f<frame> pc lr r0-r3 and, when r1 points into RAM, the first 8 bytes at r1 (a source string).
local at = assert(CALL_AT, "set --var CALL_AT=0x...")
local from, max, n = FROM or 0, CALL_MAX or 40, 0
local function rd(a) return emu.read(a, emu.memType.gbaMemory) end
L.on_exec(at, at, function()
  if L.frame < from or n >= max then return end
  n = n + 1
  local s = emu.getState()
  local r1 = s["cpu.r1"]
  local bytes = ""
  if r1 >= 0x02000000 and r1 < 0x09000000 then
    for i = 0, 7 do bytes = bytes .. string.format("%02X", rd(r1 + i)) end
  end
  L.log(string.format("CALL f%d pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X [r1]=%s", L.frame, at,
    s["cpu.r14"], s["cpu.r0"], r1, s["cpu.r2"], s["cpu.r3"], bytes))
end)
