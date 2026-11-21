-- ramdump_at.lua: dump EWRAM+IWRAM to OUT/ram.bin at frame DUMP_AT (default 60), then stop. Used to find RAM no
-- mode touches (tools/vwf.py keeps its state there).
local AT = DUMP_AT or 60
L.on_frame(function(n)
  if n == AT then L.dump_ram("ram.bin"); L.finish(0) end
end)
