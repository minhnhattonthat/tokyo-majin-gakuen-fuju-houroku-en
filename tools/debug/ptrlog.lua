-- ptrlog.lua: each frame read the u32 pointer PTR and the u16 fields at OFFS (list of offsets) behind it; log a line
-- whenever the pointer or any field changes. Follows a mode's state struct through a flow:
--   --script tools/debug/ptrlog.lua --var PTR=0x030035B8 --var "OFFS={0x36,0x38}"
local M = emu.memType.gbaMemory
local ptr = assert(PTR, "set --var PTR=0x...")
local offs = OFFS or {0}
local function r16(a) return emu.read(a, M) | (emu.read(a + 1, M) << 8) end
local function r32(a) return r16(a) | (r16(a + 2) << 16) end
local last
L.on_frame(function(n)
  local base = r32(ptr)
  local parts = { string.format("%08X", base) }
  if base >= 0x02000000 and base < 0x03008000 then
    for _, o in ipairs(offs) do parts[#parts + 1] = string.format("+%X=%d", o, r16(base + o)) end
  end
  local s = table.concat(parts, " ")
  if s ~= last then L.log(string.format("f%d %s", n, s)); last = s end
end)
