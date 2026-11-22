-- valwrite.lua: log each write of a value into a RAM range (who queues a graphic: its ROM pointer lands in a queue).
--   emu.py ... --script tools/debug/valwrite.lua --var VAL=0x08B4F808 [--var LO=0x03000000 --var HI=0x03008000]
--   [--var FROM=0] [--var MAXN=20]
-- Matches the whole word or its low half (stores may be split into halfwords). Logs: VAL f<frame> addr value pc lr.
local val = assert(VAL, "set --var VAL=0x...")
local lo, hi, from, maxn, n = LO or 0x03000000, HI or 0x03008000, FROM or 0, MAXN or 20, 0
L.on_write(lo, hi, function(addr, value)
  if L.frame < from or n >= maxn then return end
  if value ~= val and value ~= (val & 0xFFFF) then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("VAL f%d addr=%08X value=%08X pc=%08X lr=%08X", L.frame, addr, value, L.pc(), s["cpu.r14"] or 0))
end)
