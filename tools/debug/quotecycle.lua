-- quotecycle.lua: show enemy quotes on demand (text coverage + QA shots of the quote box).
-- Quote task struct [0x030035B8]: u16 +0x34 quote index, u16 +0x38 state (jump table 0x0801C59C: 0 init, 1 portrait,
-- 2 slide in, 3 alloc + init at 0x0801C6C0, 4 print a char a frame, 5 print the rest (A), 6 wait A or 0x12B frames
-- at 0x0801C8FC, 7 slide out, 8 free + restore, 9 end at 0x0801CA60: when bl 0x08000C68 returns non-zero it calls
-- 0x0800E4BC = next battle phase). A = bit 0 of the new-press u16 0x03005530. Printer B (0x0800455C) draws each
-- glyph as sprites, so a quote can only be restarted after state 8 has freed them.
-- Opponent records 0xD6E17C (getter 0x0803D7AC, see forceopp.lua), 20 quotes each.
--   emu.py ... --script tools/debug/quotecycle.lua [--var "OPPS={0,1,2}"] [--var PER=20] [--var HOLD=30]
-- Without OPPS it only logs the game's own quotes. With OPPS, the first quote display the game makes is looped:
-- each quote waits HOLD frames in state 6 (A presses masked), a shot q<opp>_<idx>.png is taken, A closes it, and at
-- state 9 the task goes back to state 0 with the next quote (all PER quotes of each opponent in OPPS, the getter
-- forced to that opponent, so the portrait matches) instead of ending; after the last one the battle goes on.
-- board_turn.mss + work/qa/bd/rand.txt reaches a quote at f585. Logs QUOTE f<frame> opp=<n> idx=<shown>.
local M = emu.memType.gbaMemory
local per, hold = PER or 20, HOLD or 30
local opps = OPPS
local oi, qi, waited = 1, 0, 0
local cur_opp = opps and opps[1] or nil
local function task() return emu.read32(0x030035B8, M, false) end
if opps then
  L.on_exec(0x0803D7AC, 0x0803D7AC, function()
    local s = emu.getState()
    if cur_opp and s["cpu.r0"] ~= cur_opp then
      s["cpu.r0"] = cur_opp
      emu.setState(s)
    end
  end)
end
L.on_exec(0x0801C6C0, 0x0801C6C0, function()
  local t = task()
  if cur_opp then emu.write16(t + 0x34, qi, M) end
  L.log(string.format("QUOTE f%d opp=%s idx=%d", L.frame, tostring(cur_opp), emu.read16(t + 0x34, M, false)))
end)
if opps then
  local last_frame = -1
  L.on_exec(0x0801C8FC, 0x0801C8FC, function()
    if not cur_opp or L.frame == last_frame then return end
    last_frame = L.frame
    local keys = emu.read16(0x03005530, M, false)
    waited = waited + 1
    if waited < hold then
      if keys & 1 ~= 0 then emu.write16(0x03005530, keys & 0xFFFE, M) end
    elseif waited == hold then
      L.shot(string.format("q%02d_%02d.png", cur_opp, qi))
      emu.write16(0x03005530, keys | 1, M)
    end
  end)
  -- state 9, after bl 0x08000C68: r0 ~= 0 would end the quote; restart at state 0 with the next quote instead
  L.on_exec(0x0801CA64, 0x0801CA64, function()
    if not cur_opp then return end
    local s = emu.getState()
    if s["cpu.r0"] == 0 then return end
    waited = 0
    qi = qi + 1
    if qi >= per then
      qi = 0
      oi = oi + 1
      cur_opp = opps[oi]
    end
    if not cur_opp then L.log(string.format("QUOTE f%d done", L.frame)) return end
    s["cpu.r0"] = 0
    emu.setState(s)
    emu.write16(task() + 0x38, 0, M)
  end)
end
