-- loadcheck.lua: after 続きから, log each game-mode change with the chapter byte and both name fields (hex), so
-- save.py test can assert that an edited save loaded (mode 6 = hub, chapter = the save's) with no corruption path.
local M = emu.memType.gbaMemory
local function hex(a, n)
  local t = {}
  for i = 0, n - 1 do t[#t + 1] = string.format("%02X", emu.read(a + i, M)) end
  return table.concat(t)
end
L.on_write(0x03003828, 0x03003828, function(addr, v)
  if v == 0 then return end
  -- the store has not landed yet; read the rest on the next frame
  local f = L.frame
  local fired = false
  L.on_frame(function(n)
    if fired or n < f + 1 then return end
    fired = true
    L.log(string.format("LOAD f%d mode=%d ch=%d surname=%s name=%s", n, v, emu.read(0x03005AA8, M),
      hex(0x03003830, 8), hex(0x03005A70, 8)))
  end)
end)
