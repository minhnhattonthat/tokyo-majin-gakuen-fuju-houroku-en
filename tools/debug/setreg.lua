-- setreg.lua: log, and optionally overwrite, a register each time the CPU executes an address
-- (force a branch: e.g. a screen's sub-state switch).
--   emu.py ... --script tools/debug/setreg.lua --var AT=0x0805BF74 --var REG=7 [--var VAL=2] [--var MAX=20]
-- Logs: SETREG f<frame> pc r<REG>=<old> -> <new> lr sp. Without VAL it only logs.
local at = assert(AT, "set --var AT=0x...")
local reg = "cpu.r" .. tostring(REG or 0)
local max, n = MAX or 20, 0
L.on_exec(at, at, function()
  local s = emu.getState()
  local old = s[reg]
  if VAL ~= nil then
    s[reg] = VAL
    emu.setState(s)
  end
  if n < max then
    n = n + 1
    L.log(string.format("SETREG f%d pc=%08X %s=%08X -> %08X lr=%08X sp=%08X", L.frame, at, reg, old,
      VAL or old, s["cpu.r14"], s["cpu.r13"]))
  end
end)
