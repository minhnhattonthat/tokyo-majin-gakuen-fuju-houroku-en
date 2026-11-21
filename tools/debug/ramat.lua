-- ramat.lua: dump EWRAM+IWRAM (L.dump_ram) at each frame in RAM_AT (Lua table), as ram_<frame>.bin in --out.
--   --script tools/debug/ramat.lua --var "RAM_AT={6000,9000}"
local at = {}
for _, f in ipairs(RAM_AT or {}) do at[f] = true end
L.on_frame(function(n)
  if at[n] then L.dump_ram(string.format("ram_%06d.bin", n)) end
end)
