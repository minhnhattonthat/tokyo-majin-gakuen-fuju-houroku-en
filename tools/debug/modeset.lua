-- modeset.lua: at frame AT write mode TO (u16 0x03003828), optional param PARAM (0x03005668). Leaves a screen that
-- has no reachable exit (e.g. the pack-opening screen) for another mode with the RAM kept:
--   covrun.py NAME --state-in work/states/shop_after_pack.mss --route-str ".." --script tools/debug/modeset.lua
--             --var AT=300 --var TO=9
-- See modeswap.lua for the swap-on-entry variant.
local MODE_ADDR, PARAM_ADDR = 0x03003828, 0x03005668
local at = assert(AT, "set --var AT=<frame>")
local to = assert(TO, "set --var TO=<mode>")
local M = emu.memType.gbaMemory
local function w16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end
L.on_frame(function(n)
  if n ~= at then return end
  if PARAM then w16(PARAM_ADDR, PARAM) end
  w16(MODE_ADDR, to)
  L.log(string.format("f%d modeset -> %d", n, to))
end)
