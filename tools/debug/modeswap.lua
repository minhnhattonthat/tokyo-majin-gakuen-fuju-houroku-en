-- modeswap.lua: when the game enters mode FROM (u16 0x03003828), switch it to mode TO (param PARAM in 0x03005668)
-- on the next frame. Lets a loaded save (its RAM: card collection, names, chapter) reach any mode, e.g. the shop:
--   emu.py build/tmgfh_en.gba --sav work/saves/allcards.sav --route tools/routes/title_continue.txt
--          --script tools/debug/modeswap.lua --var FROM=6 --var TO=9
-- warp.py's MODE warps fire on New Game instead, so the RAM there is a fresh game's.
-- ONCE (default true): only the first entry of FROM is swapped.
local MODE_ADDR, PARAM_ADDR = 0x03003828, 0x03005668
local from = assert(FROM, "set --var FROM=<mode>")
local to = assert(TO, "set --var TO=<mode>")
local once = ONCE ~= false
local M = emu.memType.gbaMemory
local function w16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end
local pending, fired = false, false
L.on_write(MODE_ADDR, MODE_ADDR, function(_, v)
  if v ~= from or (once and fired) then return end
  pending, fired = true, true
end)
L.on_frame(function(n)
  if not pending then return end
  pending = false
  if PARAM then w16(PARAM_ADDR, PARAM) end
  w16(MODE_ADDR, to)
  L.log(string.format("f%d modeswap %d -> %d", n, from, to))
end)
