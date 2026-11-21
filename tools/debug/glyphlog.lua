-- glyphlog.lua: log the text drawn through the per-cell glyph routine 0x08003B84 (every text printer uses it).
-- Consecutive calls (r0 = previous r0 + 2) form one string; each distinct (caller, string) is logged once as
--   GLYPH f<frame> lr=<caller> <unit hex, 4 digits each, low byte first as in ROM>
-- tools/glyphs.py decodes these (VWF units through the build's MTE table, Shift-JIS, control codes).
-- GLYPH_RAW=1 logs every call with its registers instead (cell layout work). GLYPH_MAX caps the lines (20000).
local MAX = GLYPH_MAX or 20000
local n = 0
local seen = {}
local cur, last_r0, cur_lr, cur_f = {}, -10, 0, 0
local function rd(a) return emu.read(a, emu.memType.gbaMemory) end
local function flush()
  if #cur == 0 then return end
  local s = table.concat(cur)
  local key = string.format("%08X ", cur_lr) .. s
  if not seen[key] and n < MAX then
    seen[key] = true
    n = n + 1
    L.log(string.format("GLYPH f%d lr=%08X %s", cur_f, cur_lr, s))
  end
  cur = {}
end
L.on_exec(0x08003B84, 0x08003B84, function()
  local s = emu.getState()
  local r0 = s["cpu.r0"]
  if GLYPH_RAW then
    if n < MAX then
      n = n + 1
      L.log(string.format("f%d lr=%08X r0=%08X u=%02X%02X r1=%08X r2=%08X r3=%X", L.frame, s["cpu.r14"], r0,
        rd(r0), rd(r0 + 1), s["cpu.r1"], s["cpu.r2"], s["cpu.r3"]))
    end
    return
  end
  if r0 ~= last_r0 + 2 or s["cpu.r14"] ~= cur_lr then
    flush()
    cur_lr, cur_f = s["cpu.r14"], L.frame
  end
  cur[#cur + 1] = string.format("%02X%02X", rd(r0), rd(r0 + 1))
  last_r0 = r0
end)
L.on_frame(function() if L.frame % 30 == 0 then flush(); last_r0 = -10 end end)
