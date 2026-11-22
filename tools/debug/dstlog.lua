-- dstlog.lua: who fills a VRAM/RAM range? Logs each BIOS SWI (CpuSet/CpuFastSet/decompress) whose destination r1
-- range covers DST_LO..DST_HI, and each direct CPU write there (pc outside the BIOS), with the value.
--   emu.py ... --script tools/debug/dstlog.lua --var DST_LO=0x0600FA8E [--var DST_HI=0x0600FAD1] [--var FROM=0]
--              [--var DST_MAX=200]
-- Logs: SWI f<frame> lr r0 r1 r2 (+ swi number) / CPU f<frame> pc lr addr value.
local lo = assert(DST_LO, "set --var DST_LO=0x...")
local hi, from, max, n = DST_HI or lo, FROM or 0, DST_MAX or 200, 0
local function rd8(a) return emu.read(a, emu.memType.gbaMemory) end
L.on_exec(0x00000008, 0x00000008, function()
  if L.frame < from or n >= max then return end
  local s = emu.getState()
  local r1, r2, lr = s["cpu.r1"], s["cpu.r2"], s["cpu.r14"]
  local swi = rd8(lr - 2) -- Thumb SWI: low byte of the instruction before lr
  local len
  if swi == 0x0B or swi == 0x0C then -- CpuSet / CpuFastSet: count in r2 bits 0-20, word size from bit 26
    local cnt = r2 & 0x1FFFFF
    len = ((swi == 0x0C or (r2 & 0x04000000) ~= 0) and 4 or 2) * cnt
  else
    len = 0x10000 -- decompressors: size unknown here, assume large
  end
  if r1 + len <= lo or r1 > hi then return end
  n = n + 1
  L.log(string.format("SWI%02X f%d lr=%08X r0=%08X r1=%08X r2=%08X", swi, L.frame, lr, s["cpu.r0"], r1, r2))
end)
L.on_write(lo, hi, function(addr, value)
  if L.frame < from or n >= max then return end
  local pc = L.pc()
  if pc < 0x4000 then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("CPU f%d pc=%08X lr=%08X addr=%08X val=%s", L.frame, pc, s["cpu.r14"], addr, tostring(value)))
end)
