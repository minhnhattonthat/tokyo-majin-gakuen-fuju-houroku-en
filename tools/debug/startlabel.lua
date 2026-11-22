-- startlabel.lua: start the warped story scene at label LABEL instead of label 0 (the parts a chapter plays after
-- its battle, or any later part of a scene).
--   warp.py B18 --mash 4 --script tools/debug/startlabel.lua --var LABEL=12
-- The story loader 0x0803F3B4 seeks to label index byte [[0x03007570] + 4] (the offset table entry, label 0 = body
-- start; op 09 nn stores nn - 1 there and the loader runs again). The first loader call after the warp gets r1 =
-- LABEL at 0x0803F3EC (just after it read the byte); later calls (gotos) are left alone.
local label = assert(LABEL, "set --var LABEL=n")
local done = false
L.on_exec(0x0803F3EC, 0x0803F3EC, function()
  if done then return end
  local s = emu.getState()
  L.log(string.format("STARTLABEL f%d game=%d forced=%d", L.frame, s["cpu.r1"], label))
  s["cpu.r1"] = label
  emu.setState(s)
  done = true
end)
