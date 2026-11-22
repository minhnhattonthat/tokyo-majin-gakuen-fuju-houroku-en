-- popcycle.lua: show any list of strings in the battle popup (text coverage + QA shots of the popup box).
-- The popup printer 0x08018AB0 (r0 = string, r1 = x, r2 = y, r3 = flag; strings of the message table 0x08D7A700 and its
-- sub-tables: battle prompts, ability / possession / barrier / spell / land effect texts) is called rarely in a
-- battle (board_turn.mss + work/qa/bd/rand.txt: f685 + f1073 turn banner = box type 10, the effect popups' box: the
-- default; f2658 a smaller 2-line prompt box at x 56 y 88 = SKIP=2). At call SKIP+1 this saves a state, then for each
-- address in LIST (a text file, one hex build address per line, e.g. from build/strings.tsv) it loads that state,
-- swaps r0 for the address, runs HOLD frames, and takes p<NNN>_<addr>.png. Logs POPSTR f<frame> i=<n> addr=<a>.
--   emu.py build/tmgfh_en.gba --state-in work/states/board_turn.mss --route work/qa/bd/rand.txt
--     --script tools/debug/popcycle.lua --var "LIST='C:/.../list.txt'" [--var HOLD=40] [--frames ...]
-- Frames needed: ~685 + count * (HOLD + 2). The game's own A presses (route) are masked while cycling.
local M = emu.memType.gbaMemory
local hold = HOLD or 40
local addrs = {}
for ln in L.read_file(assert(LIST, "set --var LIST='path'")):gmatch("[^\r\n]+") do
  local a = ln:match("^%s*(%x+)")
  if a then addrs[#addrs + 1] = tonumber(a, 16) | 0x08000000 end
end
local base = OUT .. "popbase.mss"
local i, waiting, started = 0, 0, false
local function next_one()
  i = i + 1
  if i > #addrs then
    L.log(string.format("POPSTR f%d done %d", L.frame, #addrs))
    L.finish(0)
    return
  end
  -- the state was saved at 0x08018AB2 (after the push; r0 = string, untouched until 0x08018ABC)
  L.load_state(base, function()
    local s = emu.getState()
    s["cpu.r0"] = addrs[i]
    emu.setState(s)
    waiting = hold
    L.log(string.format("POPSTR f%d i=%d addr=%08X pc=%08X", L.frame, i, addrs[i], s["cpu.r15"]))
  end)
end
-- The turn banner (SKIP=0) uses box type 10, the same as the ability / effect popups (0x0801A8DC(10, 0x30, y)), but
-- prints its name lines (y 0x78, 0x88) after the popup string with 0x08018B4C from 0x080100FC..0x0801018A: those
-- calls get an empty string, so only the cycled string shows.
L.on_exec(0x08018B4C, 0x08018B4C, function()
  if not started then return end
  local s = emu.getState()
  local lr = s["cpu.r14"]
  if lr >= 0x080100FC and lr <= 0x0801018F then
    emu.write16(0x0203FFF0, 0, M)
    s["cpu.r0"] = 0x0203FFF0
    emu.setState(s)
  end
end)
-- once cycling, no route input reaches the game (a stray L opens the card view, B closes the popup)
emu.addEventCallback(L.safe(function() if started then emu.setInput({}, 0) end end), emu.eventType.inputPolled)
local skip = SKIP or 0
L.on_exec(0x08018AB0, 0x08018AB0, function()
  if started then return end
  if skip > 0 then skip = skip - 1 return end
  started = true
  L.save_state(base, function() next_one() end)
end)
L.on_frame(function()
  if waiting > 0 then
    emu.write16(0x03005530, 0, M)
    waiting = waiting - 1
    if waiting == 0 then
      L.shot(string.format("p%03d_%07X.png", i, addrs[i] & 0xFFFFFFF))
      next_one()
    end
  end
end)
