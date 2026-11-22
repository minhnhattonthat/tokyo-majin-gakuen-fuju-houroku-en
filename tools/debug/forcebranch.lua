-- forcebranch.lua: force every story-scene branch to option BRANCH (0-based), so a mash run reads that branch's lines.
--   warp.py B18 --mash 4 --script tools/debug/forcebranch.lua --var BRANCH=1
-- Scene branch ops (docs/re/text.md §Story scene format) each call a helper, then use r0 as the index into the
-- `09 nn` goto list that follows the op; here r0 is rewritten right after the helper returns:
--   0A emotion choice (9 ways)  exec 0x0803FEAC, bl 0x0805F7D0 returns -1 while waiting -> hook 0x0803FEB2
--   0F text choice (nn ways)    exec 0x08040160, bl 0x0805FAFC returns -1 while waiting -> hook 0x08040166
--   08 flag test (2 ways)       exec 0x0803FFFC, bl 0x0805E204                          -> hook 0x08040014
--   01 stat test (2 ways)       exec 0x0804008C, bl 0x0805E160                          -> hook 0x080400AE
-- The index is BRANCH mod the op's way count; 0F's count is the nn byte of the current op ([[0x03007570]] + 1).
local k = assert(BRANCH, "set --var BRANCH=n")
local M = emu.memType.gbaMemory
local function force(ways_fn, tag)
  return function()
    local s = emu.getState()
    local r0 = s["cpu.r0"]
    if r0 == 0xFFFFFFFF or r0 == -1 then return end
    local ways = ways_fn()
    local want = k % ways
    if r0 ~= want then
      s["cpu.r0"] = want
      emu.setState(s)
    end
    L.log(string.format("BRANCH f%d %s game=%d forced=%d", L.frame, tag, r0, want))
  end
end
L.on_exec(0x0803FEB2, 0x0803FEB2, force(function() return 9 end, "0A"))
L.on_exec(0x08040166, 0x08040166, force(function()
  local op = emu.read32(emu.read32(0x03007570, M, false), M, false)
  return math.max(1, emu.read(op + 1, M))
end, "0F"))
L.on_exec(0x08040014, 0x08040014, force(function() return 2 end, "08"))
L.on_exec(0x080400AE, 0x080400AE, force(function() return 2 end, "01"))
