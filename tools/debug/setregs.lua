-- setregs.lua: setreg.lua for several addresses at once (force a chain of branches in one run).
--   emu.py ... --script tools/debug/setregs.lua --var "SETS={[0x08043272]={0,4},[0x0804D958]={0,0xFFFFFFFF}}"
--   [--var MAX=20]
-- SETS maps an address to {register number, value}: each time the CPU executes the address the register is
-- overwritten. Logs: SETREG f<frame> pc r<N>=<old> -> <new> lr (first MAX hits per address).
-- Example (session 31): 0x08043272 r0=4 opens the shop's Sell as the discard list (sub-mode 4);
-- 0x0804D958 r0=-1 makes the discard check answer "the Dragon Heir card" (D72C40).
local sets = assert(SETS, "set --var SETS={[0xADDR]={reg,val},..}")
local max = MAX or 20
for at, rv in pairs(sets) do
  local reg, val, n = "cpu.r" .. tostring(rv[1]), rv[2], 0
  L.on_exec(at, at, function()
    local s = emu.getState()
    local old = s[reg]
    s[reg] = val
    emu.setState(s)
    if n < max then
      n = n + 1
      L.log(string.format("SETREG f%d pc=%08X %s=%08X -> %08X lr=%08X", L.frame, at, reg, old, val, s["cpu.r14"]))
    end
  end)
end
