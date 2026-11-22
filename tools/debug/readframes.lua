-- readframes.lua: log each frame (at most once per frame and address) on which a ROM/RAM range is read, with the
-- address: when does the game use this table? (watch.lua logs each PC only once.)
--   emu.py ... --script tools/debug/readframes.lua --var WATCH_LO=0x08D7A6D0 --var WATCH_HI=0x08D7A6FF
local lo = assert(WATCH_LO, "set --var WATCH_LO=0x...")
local hi = WATCH_HI or lo
local seen = {}
L.on_read(lo, hi, function(addr)
  local key = L.frame * 0x10000000 + (addr - lo)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d read %08X", L.frame, addr))
end)
