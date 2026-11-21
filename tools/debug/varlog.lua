-- varlog.lua: log every value change written to VAR_LO..VAR_HI (byte granularity): frame, pc, addr, value.
--   emu.py ... --script tools/debug/varlog.lua --var VAR_LO=0x03005AA8 [--var VAR_HI=0x03005AAB]
-- Unlike watch.lua (one line per PC) this logs each change, so a story counter's whole history shows.
local lo = assert(VAR_LO, "set --var VAR_LO=0x...")
local hi = VAR_HI or lo
local last = {}
L.on_write(lo, hi, function(addr, v)
  if last[addr] == v then return end
  last[addr] = v
  L.log(string.format("f%d pc=%08X addr=%08X v=%02X", L.frame, L.pc(), addr, v or -1))
end)
