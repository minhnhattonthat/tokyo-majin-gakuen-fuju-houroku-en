-- popuplog.lua: log calls to the battle popup printer 0x08018AB0 (r0 = string, r1 = x, r2 = y, r3 = flag; strings come
-- from the message table 0x08D7A700, e.g. 0x0800F21A). Logs POP f<frame> str=<r0> x y flag lr=<caller>.
--   emu.py ... --script tools/debug/popuplog.lua [--var FN=0x08018AB0]
local fn = FN or 0x08018AB0
L.on_exec(fn, fn, function()
  local s = emu.getState()
  L.log(string.format("POP f%d str=%08X x=%d y=%d flag=%d lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"], s["cpu.r2"],
    s["cpu.r3"], s["cpu.r14"]))
end)
