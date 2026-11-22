-- forceopp.lua: make the battle opponent OPP (0-42, records at 0xD6E17C, 12 bytes: u32 quote list, u16 char,
-- u16 life, u32 level; getter 0x0803D7AC). The index is the byte at [0x0300756C] + 0x7F1; mode-1 setup
-- (0x0800E7A4..) reads it through the getter. This pokes the byte every frame and rewrites the getter's r0, so a
-- battle set up (or rematched) after the poke uses opponent OPP: its portrait, life and quote list (20 quotes).
--   emu.py ... --script tools/debug/forceopp.lua --var OPP=5
-- Logs OPP f<frame> old=<n> once per change seen, and GET f<frame> lr=<caller> for the first CALL_MAX getter calls.
local opp = assert(OPP, "set --var OPP=n")
local M = emu.memType.gbaMemory
local last, n, max = -1, 0, CALL_MAX or 20
L.on_frame(function()
  local base = emu.read32(0x0300756C, M, false)
  if base < 0x02000000 or base >= 0x04000000 then return end
  local a = base + 0x7F1
  local v = emu.read(a, M)
  if v ~= opp then
    if v ~= last then L.log(string.format("OPP f%d old=%d", L.frame, v)) end
    last = v
    emu.write(a, opp, M)
  end
end)
L.on_exec(0x0803D7AC, 0x0803D7AC, function()
  local s = emu.getState()
  if n < max then
    n = n + 1
    L.log(string.format("GET f%d lr=%08X r0=%d", L.frame, s["cpu.r14"], s["cpu.r0"]))
  end
  if s["cpu.r0"] ~= opp then
    s["cpu.r0"] = opp
    emu.setState(s)
  end
end)
