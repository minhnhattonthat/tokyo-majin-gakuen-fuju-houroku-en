-- scenelog.lua: log each story-scene lookup, by hooking reads of the scene tables (exec hooks on the getters
-- 0x0805E2DC / 0x0805E2F8 did not fire in Mesen GBA). Table B 0x08D82078 (40 u32, by chapter byte 0x03005AA8),
-- table A 0x08D8211C (130 u32, group*10 + slot). Logs frame, table, index, chapter byte, caller (lr).
local CH = 0x03005AA8
local function rd(a) return emu.read(a, emu.memType.gbaMemory) end
local function hit(tag, base)
  return function(addr)
    if (addr - base) % 4 ~= 0 then return end
    local s = emu.getState()
    L.log(string.format("f%d %s[%d] ch=%d lr=%08X", L.frame, tag, (addr - base) // 4, rd(CH), s["cpu.r14"] or -1))
  end
end
L.on_read(0x08D82078, 0x08D82117, hit("B", 0x08D82078))
L.on_read(0x08D8211C, 0x08D82323, hit("A", 0x08D8211C))
