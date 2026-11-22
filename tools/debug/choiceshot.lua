-- choiceshot.lua: screenshot a text choice (op 0F) while it waits for input, for inkbox.py.
--   warp.py B02 --mash 40 --script tools/debug/startlabel.lua --var LABEL=8 --script tools/debug/choiceshot.lua
-- The 0F choice helper 0x0805FAFC runs every frame while the box is up (docs/re/text.md); a shot is taken on the
-- 2nd, 8th, 14th .. frame it runs (choice_fNNNNN.png in the run dir), at most MAX (default 6) shots.
local max = MAX or 6
local last, hits, n = -1, 0, 0
L.on_exec(0x0805FAFC, 0x0805FAFC, function()
  if L.frame == last or n >= max then return end
  last = L.frame
  hits = hits + 1
  if hits % 6 == 2 then
    n = n + 1
    L.shot(string.format("choice_f%05d.png", L.frame))
    L.log(string.format("CHOICESHOT f%d", L.frame))
  end
end)
