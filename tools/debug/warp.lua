-- warp.lua: cold boot -> any story scene, by id. Run with the newgame route (or tools/debug/warp.py NAME).
--   emu.py ROM --out DIR --route tools/routes/newgame.txt --script tools/debug/warp.lua --var "SCENE='B05'"
-- SCENE forms:
--   B<n>     story scene of chapter n (table B 0x08D82078[n], n = 0..39); the chapter byte 0x03005AA8 = n.
--   A<g>.<s> event scene: table A 0x08D8211C[g*10+s] (g = 0..12, s = 0..9); flag 0x01000000 set, slot 0x03003580.
--   MODE<m>[.<p>] jump straight to game mode m (handler table 0x08D7A424) with param p in 0x03005668 (menus).
--   WAIT<m>  no warp: the route drives the game; passes once the game itself enters mode m.
-- Optional: CH=<n> overrides the chapter byte for MODE/A warps.
-- How: the title's New Game writes mode 2 (story) to 0x03003828. On that write we set the chapter byte, the event
-- flag and slot (or the mode), so the story loader (0x0803F3B4) picks our scene. Proof: the loader's table read is
-- logged as "WARP ok <table>[<index>]"; a run whose log lacks it went somewhere else.
local MODE, CHAP, PARAM = 0x03003828, 0x03005AA8, 0x03005668
local CH_OVERRIDE = CH
local FLAGS, SLOT = 0x0300382C, 0x03003580
local EVENT = 0x01000000
local M = emu.memType.gbaMemory
-- byte-wise only: Mesen's write16/write32 raised "value out of range" here
local function w8(a, v) emu.write(a, v & 0xFF, M) end
local function w16(a, v) w8(a, v); w8(a + 1, v >> 8) end
local function r32(a) return emu.read(a, M) | emu.read(a + 1, M) << 8 | emu.read(a + 2, M) << 16 | emu.read(a + 3, M) << 24 end
local function w32(a, v) for i = 0, 3 do w8(a + i, v >> (8 * i)) end end

-- chapter whose free-time block uses event group g (from the switch at 0x0805E2FC); group 12 = any other chapter
local GROUP_CH = { [0] = 2, 5, 8, 11, 14, 18, 21, 24, 27, 32, 35, 37, 0 }

local spec = assert(SCENE, "set --var \"SCENE='B05'\"")
local kind, want_tab, want_idx, ch, slot, mode, param
do
  local n = spec:match("^[Bb](%d+)$")
  local g, s = spec:match("^[Aa](%d+)%.(%d+)$")
  local m, p = spec:match("^MODE(%d+)%.?(%d*)$")
  local wm = spec:match("^WAIT(%d+)$")
  if wm then
    -- no warp: the route drives the game; pass when it writes mode wm (title submenus, load screen...)
    local want = tonumber(wm)
    local hit = false
    L.on_write(MODE, MODE, function(addr, v)
      if not hit and v == want then
        hit = true
        L.log(string.format("f%d WARP ok WAIT%d", L.frame, want))
      end
    end)
    kind = "WAIT"
  elseif n then
    kind, ch, want_tab, want_idx = "B", tonumber(n), "B", tonumber(n)
    assert(ch <= 39, "chapter 0..39")
  elseif g then
    g, s = tonumber(g), tonumber(s)
    assert(g <= 12 and s <= 9, "A<0..12>.<0..9>")
    kind, ch, slot, want_tab, want_idx = "A", GROUP_CH[g], s, "A", g * 10 + s
  elseif m then
    kind, mode, param = "MODE", tonumber(m), tonumber(p ~= "" and p or "0")
  else
    error("bad SCENE " .. spec)
  end
  if CH_OVERRIDE then ch = CH_OVERRIDE end
end

local done = false
L.on_write(MODE, MODE + 1, function(addr, v)
  if done or kind == "WAIT" or addr ~= MODE or v ~= 2 then return end
  done = true
  if ch then w8(CHAP, ch) end
  if kind == "A" then
    w32(FLAGS, r32(FLAGS) | EVENT | (1 << slot)); w8(SLOT, slot)
  elseif kind == "MODE" then
    w16(PARAM, param)
    -- the CPU's own store lands after this callback, so re-write the mode on the next frame
  end
  L.log(string.format("f%d WARP %s ch=%s slot=%s", L.frame, spec, tostring(ch), tostring(slot)))
end)

local pending_mode = kind == "MODE"
L.on_frame(function(n)
  if done and pending_mode then
    pending_mode = false
    w16(MODE, mode)
    L.log(string.format("f%d WARP ok MODE%d.%d", n, mode, param))
  end
end)

if want_tab then
  local base = want_tab == "B" and 0x08D82078 or 0x08D8211C
  local hi = want_tab == "B" and 0x08D82117 or 0x08D82323
  local seen = false
  L.on_read(base, hi, function(addr)
    if seen or not done or (addr - base) % 4 ~= 0 then return end
    seen = true
    local idx = (addr - base) // 4
    L.log(string.format("f%d WARP %s %s[%d]", L.frame, idx == want_idx and "ok" or "WRONG", want_tab, idx))
  end)
end
