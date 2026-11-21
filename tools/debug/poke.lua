-- poke.lua: hold u16 values in RAM every frame from POKE_FROM on (cheat-style), for god mode or forced defeat tests.
--   --script tools/debug/poke.lua --var "POKES={[0x020041B2]=1}" [--var POKE_FROM=2600] [--var POKE_TO=9000]
local M = emu.memType.gbaMemory
local from, to = POKE_FROM or 0, POKE_TO or math.huge
L.on_frame(function(n)
  if n < from or n > to then return end
  for a, v in pairs(POKES or {}) do
    emu.write(a, v & 0xFF, M)
    emu.write(a + 1, (v >> 8) & 0xFF, M)
  end
end)
