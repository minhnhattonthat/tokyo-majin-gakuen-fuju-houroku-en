-- onmode.lua: queue scripted presses each time the game enters a mode (mode u16 0x03003828), e.g. pick 先に進む
-- whenever the hub opens (mash A alone picks 寄り道) or leave the name entry. Mash resumes once the presses end.
--   emu.py ... --mash 20 --script tools/debug/onmode.lua --var "ON_ROUTES={[6]='90 -;6 down;30 -;6 a;120 -'}"
-- ON_ROUTES: {[mode] = 'frames buttons;...'}. ON_ONCE=true fires each mode's presses only on its first entry.
-- ON_SAVE='C:/abs/dir': also save a state <dir>/mode<m>_<n>.mss on each entry (the frame the mode is set).
-- Routes that worked from a fresh new game (warps skip the opening's deck setup, so mode 1 hangs after them):
--   [4]='300 -;6 right;40 -;6 right;40 -;6 a;150 -'  name entry: keep 緋勇 龍麻 (終了), mash A answers the rest
--   [6]='400 -;6 up;40 -;6 a;300 -'                  hub: cursor starts on the first item, up wraps to 先に進む
local MODE_ADDR = 0x03003828
local routes = assert(ON_ROUTES, "set --var \"ON_ROUTES={[6]='frames buttons;...'}\"")
local seen = {}
L.on_write(MODE_ADDR, MODE_ADDR, function(_, v)
  local route = routes[v]
  if not route then return end
  seen[v] = (seen[v] or 0) + 1
  if ON_ONCE and seen[v] > 1 then return end
  L.log(string.format("f%d onmode: mode %d entry %d", L.frame, v, seen[v]))
  if ON_SAVE then L.save_state(string.format("%s/mode%d_%d.mss", ON_SAVE, v, seen[v])) end
  for step in route:gmatch("[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    L.press(spec, tonumber(n))
  end
end)
