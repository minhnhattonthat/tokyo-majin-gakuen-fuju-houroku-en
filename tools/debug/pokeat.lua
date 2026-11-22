-- pokeat.lua: at frame AT write u16 values once. POKES maps an address to a value; PPOKES maps a pointer address to
-- {offset, value} and writes the u16 at [u32 at the pointer] + offset (state structs behind a pointer, e.g. the
-- pack screen's substate [0x030035B8]+0x38). Unlike poke.lua, nothing is held after AT.
--   --script tools/debug/pokeat.lua --var AT=400 --var "POKES={[0x03003818]=5008}"
--   --var "PPOKES={[0x030035B8]={0x38,7}}"
local M = emu.memType.gbaMemory
local at = assert(AT, "set --var AT=<frame>")
local function w16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end
local function r32(a)
  return emu.read(a, M) | (emu.read(a + 1, M) << 8) | (emu.read(a + 2, M) << 16) | (emu.read(a + 3, M) << 24)
end
L.on_frame(function(n)
  if n ~= at then return end
  for a, v in pairs(POKES or {}) do w16(a, v) end
  for p, ov in pairs(PPOKES or {}) do
    local base = r32(p)
    w16(base + ov[1], ov[2])
    L.log(string.format("f%d poke [%08X]=%08X +%X = %d", n, p, base, ov[1], ov[2]))
  end
end)
