"""tut_compose.py: compose the English battle-tutorial screens (S29) into gfx/tutorial/<ENTRY>.png (one-off; the
build reads only the PNGs, through tools/gfx_tutorial.py).

    python -X utf8 tools/debug/tut_compose.py [--check]

Sources: the JP screens of the table 0xD63288-0xD635F8 (rom/base.gba), the game's own VWF font (tools/vwf.py, the
font the real card panel uses) and pieces of two English card-panel shots that are kept in gfx/tutorial/ref_*.png
(the plates BATTLE / Leaf, the bracket row and the 1-2-3 row with its moon icon, the stat rows). Every PNG is an
indexed image in the screen's own palette, so the build maps pixels 1:1. The highlight overlays (pink frames over
panel pieces) are rebuilt from the English panel, quantized to the overlay's 16 colours.

The tutorial card is 格闘家 "Fighter" (mini label FIGHTER, element 火 "Fi"), abilities 【吹飛】【庇う】 = Blst / Cov,
Mani abilities 1貫通 2必{I024} 3変生 = 1Prce 2B(moon) 3Mrph (cf.tsv CF6558-CF6770 labels), trigger "Took 40 dmg",
effects +20 AT, +10 HP, +0 SP: the same wording the real panel prints for that card.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import gfx_icons          # noqa: E402
import gfx_minilabels     # noqa: E402
import gfx_frames         # noqa: E402
import vwf                # noqa: E402

OUT = ROOT / 'gfx' / 'tutorial'
PANEL = 0xD635E8          # 8bpp card panel (64 colours)
INK, SHADOW = 63, 1       # panel: white text, black shadow (as the JP glyphs)


def load(rom, e):
    """table entry -> (bpp, palette rgb list, canvas of indices)"""
    p, ps, t, ts, m, _ = struct.unpack_from('<6I', rom, e)
    p, t, m = p & 0x1FFFFFF, t & 0x1FFFFFF, m & 0x1FFFFFF
    n = (ps & 0xFFFF) // 2
    pal = [struct.unpack_from('<H', rom, p + 2 * i)[0] for i in range(n)]
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in pal]
    ents = struct.unpack_from('<600H', rom, m)
    bpp = 8 if n > 16 else 4
    cv = [[0] * 240 for _ in range(160)]
    for i, x in enumerate(ents):
        tn, hf, vf = x & 0x3FF, x >> 10 & 1, x >> 11 & 1
        for y in range(8):
            for xx in range(8):
                sx, sy = (7 - xx if hf else xx), (7 - y if vf else y)
                if bpp == 8:
                    v = rom[t + tn * 64 + sy * 8 + sx]
                else:
                    v = (rom[t + tn * 32 + sy * 4 + sx // 2] >> (4 * (sx & 1))) & 15
                cv[i // 30 * 8 + y][i % 30 * 8 + xx] = v
    return bpp, pal, cv


def save(cv, pal, e):
    im = Image.new('P', (240, 160))
    flat = [c for rgb in pal for c in rgb]
    im.putpalette(flat + [0] * (768 - len(flat)))
    im.putdata([v for row in cv for v in row])
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f'{e:06X}.png')


def nearest(pal, rgb, skip0=True):
    best = None
    for i, c in enumerate(pal):
        if skip0 and i == 0:
            continue
        dd = sum((a - b) ** 2 for a, b in zip(c, rgb))
        if best is None or dd < best[0]:
            best = (dd, i)
    return best[1]


def paste_png(cv, pal, png, box, at=None, skip_bg=False):
    """copy box (x0, y0, x1, y1) of an RGB shot into the canvas (at its own place, or at `at`), nearest colours;
    skip_bg leaves the canvas pixel where the shot shows the box's commonest colour (an icon over a background)"""
    im = Image.open(png).convert('RGB')
    px = im.load()
    x0, y0, x1, y1 = box
    dx, dy = at if at else (x0, y0)
    cols = [px[x, y] for y in range(y0, y1) for x in range(x0, x1)]
    bg = max(set(cols), key=cols.count) if skip_bg else None
    cache = {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            if c == bg:
                continue
            if c not in cache:
                cache[c] = nearest(pal, c)
            cv[dy + y - y0][dx + x - x0] = cache[c]


def wipe(cv, box, text=(INK, SHADOW)):
    """replace text pixels in box by the commonest other colour of the same row inside the box"""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        row = [v for v in cv[y][x0:x1] if v not in text]
        if not row:
            continue
        bg = max(set(row), key=row.count)
        for x in range(x0, x1):
            if cv[y][x] in text:
                cv[y][x] = bg


def clear(cv, box):
    """set every pixel of box to its panel row's background: the commonest non-text colour of x 104..239"""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        row = [v for v in cv[y][104:240] if v not in (INK, SHADOW)]
        bg = max(set(row), key=row.count)
        cv[y][x0:x1] = [bg] * (x1 - x0)


def fill(cv, box, v):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            cv[y][x] = v


FONT = None


def text(cv, x, y, s, ink=INK, shadow=SHADOW):
    """VWF text with its top cell row at y (glyph row 0 lands on y + 4, as in the game's 16 px cells)"""
    for ch in s:
        px, w, a = FONT[ch]
        for yy in range(16):
            for xx in range(16):
                v = px[yy][xx]
                if v and 0 <= x + xx < 240 and 0 <= y + yy < 160:
                    cv[y + yy][x + xx] = ink if v == 0xF else shadow
        x += a
    return x


def width(s):
    return sum(FONT[c][2] for c in s)


REF_BAT = OUT / 'ref_bat.png'    # board_turn.mss + work/qa/bd/rand.txt f1560: Giant Bat panel, plates BATTLE / Leaf
REF_GEO = OUT / 'ref_geo.png'    # hand_panel.mss + 4 x right: Geomancer panel (bracket row, 1-2-3 row with moon)


def panel(rom, en):
    bpp, pal, cv = load(rom, PANEL)
    # 青葉 -> Leaf (font text): the plate copied from the bat shot; 戦闘 -> BATTLE: the JP orange plate keeps its
    # colour, the white letters of the English sprite (bat shot) go on it
    # the plate's text centred where 青葉 was (x 200..232: the tutorial's highlight frame), not the shot's x 190
    wipe(cv, (196, 48, 238, 63))
    text(cv, (200 + 233 - width('Leaf') + 2) // 2, 47, 'Leaf')
    plate = cv[40][195]
    fill(cv, (193, 34, 237, 46), plate)
    shot = Image.open(REF_BAT).convert('RGB').load()
    for y in range(34, 46):
        for x in range(193, 237):
            if sum(shot[x, y]) >= 600:
                cv[y][x] = INK
    # mini label at the top of the card art (OBJ at x 115, y 2; visible x 5..30): FIGHTER
    cnt = {}
    for y in range(3, 8):
        for x in range(120, 146):
            cnt[cv[y][x]] = cnt.get(cv[y][x], 0) + 1
    strip = max(cnt, key=cnt.get)
    del cnt[strip]
    ink = max(cnt, key=cnt.get)
    fill(cv, (120, 3, 146, 8), strip)
    lab = gfx_minilabels.bitmap('FIGHTER')
    for y in range(8):
        for x in range(5, 31):
            if lab[y][x]:
                cv[2 + y][115 + x] = ink
    # element emblem 火 -> Fi (bottom left of the art): the near-white kanji on the disc
    # (red kanji with white glints on a peach disc, inside an orange ring: disc box x 130..137, y 49..57)
    red = lambda c: c[0] >= 150 and c[1] < 90                       # noqa: E731
    peach = lambda c: c[0] >= 200 and c[1] >= 140 and sum(c) < 600  # noqa: E731
    box = [(x, y) for y in range(49, 58) for x in range(130, 138)]
    disc = [cv[y][x] for x, y in box if peach(pal[cv[y][x]])]
    disc_c = max(set(disc), key=disc.count)
    reds = [cv[y][x] for x, y in box if red(pal[cv[y][x]])]
    white = max(set(reds), key=reds.count)            # the label ink: the kanji's red
    for x, y in box:
        c = pal[cv[y][x]]
        inner = 131 <= x <= 136 and 50 <= y <= 56         # the kanji's orange edge pixels too, not the ring
        if red(c) or sum(c) >= 600 or (inner and not peach(c)):
            cv[y][x] = disc_c
    g = [gfx_frames.SMALL['F'], gfx_frames.SMALL['i']]
    tx, ty = 131, 51
    for glyph in g:
        for yy, r in enumerate(glyph):
            for xx, c in enumerate(r):
                if c == '#':
                    cv[ty + yy][tx + xx] = white
        tx += len(glyph[0]) + 1
    # row 64: 格闘家 -> Fighter (the "12" box at x >= 222 stays)
    wipe(cv, (127, 64, 222, 80))
    text(cv, 127, 64, 'Fighter')
    # row 80: brackets row from the Geomancer shot, its labels replaced; 陽 -> sun from the same shot; fist stays
    paste_png(cv, pal, REF_GEO, (104, 80, 208, 96))
    paste_png(cv, pal, REF_GEO, (224, 80, 240, 96))
    clear(cv, (117, 81, 150, 96))
    clear(cv, (165, 81, 198, 96))
    text(cv, 119, 80, 'Blst')
    text(cv, 167, 80, 'Cov')
    # row 96: 1Maze 2B(moon) 3Prce -> 1Prce 2B(moon) 3Mrph
    paste_png(cv, pal, REF_GEO, (104, 96, 240, 112))
    clear(cv, (117, 97, 151, 112))
    clear(cv, (198, 97, 239, 112))
    text(cv, 119, 96, 'Prce')
    text(cv, 199, 96, 'Mrph')
    # row 112: 40D受けた時 -> Took 40 dmg
    wipe(cv, (108, 112, 240, 128))
    text(cv, 111, 112, 'Took 40 dmg')
    # row 128: [char]の[AT]+20 -> [char][AT]+20 (the sword icon from the bat shot, one cell left of the JP one)
    clear(cv, (127, 128, 239, 144))
    paste_png(cv, pal, REF_BAT, (127, 128, 143, 144), skip_bg=True)
    text(cv, 143, 128, '+20')
    # row 144: [HP]+10 [SP]+0 in the bat shot's layout
    paste_png(cv, pal, REF_BAT, (104, 144, 240, 160))
    clear(cv, (126, 144, 160, 160))
    clear(cv, (190, 144, 239, 160))
    text(cv, 127, 144, '+10')
    text(cv, 191, 144, '+0')
    en[PANEL] = (pal, cv)
    return pal, cv


HIGHLIGHTS = (0xD63420, 0xD63480, 0xD63498, 0xD634B0, 0xD63558)   # pink-framed copies of panel pieces
# D63558 also frames two Mani-display icons of the field screen D635D0 (no panel there): only its 1-2-3 row
HIGHLIGHT_BOX = {0xD63558: (104, 92, 240, 116)}
BUBBLES = {0xD63420: [((112, 14, 190, 37), 'Symbol'), ((193, 14, 238, 37), 'Origin'),
                      ((41, 39, 118, 62), 'Element')]}


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def rebuild_highlights(rom, e, en_panel):
    """inside every pink frame each pixel takes the English panel's pixel at its place, in the overlay's nearest
    colour. Outside = reachable from the transparent backdrop without crossing pink (bubbles and plates too); the
    frame = pink within 2 px of outside; everything else is a frame's interior (the JP 火 there is pink too)"""
    _, pal, cv = load(rom, e)
    epal, ecv = en_panel
    pinks = [i for i in range(1, 16) if pal[i][0] >= 200 and pal[i][1] < 100 and pal[i][2] >= 64]
    # seeds: the screen's edge (transparent pixels inside a frame, e.g. in the heart icon, are not outside)
    st = [(x, y) for y in range(160) for x in range(240)
          if (x in (0, 239) or y in (0, 159)) and cv[y][x] not in pinks]
    out = set(st)
    while st:
        x, y = st.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < 240 and 0 <= n[1] < 160 and n not in out and cv[n[1]][n[0]] not in pinks:
                out.add(n)
                st.append(n)
    bx0, by0, bx1, by1 = HIGHLIGHT_BOX.get(e, (0, 0, 240, 160))
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            if (x, y) in out:
                continue
            if cv[y][x] in pinks and any((x + i, y + j) in out for i in range(-2, 3) for j in range(-2, 3)):
                continue
            cv[y][x] = nearest(pal, epal[ecv[y][x]])
    return pal, cv


def plate_texture(cv):
    """the interior of the largest marble plate of an overlay: rows of pixels to tile into relettered bubbles"""
    best = None
    for y in range(160):
        run = 0
        for x in range(240):
            run = run + 1 if cv[y][x] else 0
            if run >= 100 and (best is None or run > best[2]):
                best = (x - run + 1, y, run)
    x0, y0, _ = best
    return [r[x0 + 6:x0 + 86] for r in cv[y0 + 6:y0 + 26]]


def bubble(pal, cv, box, s, tex):
    """reletter a callout bubble (rough box around it, tail excluded by width): its interior, 3 px inside the
    outline, is refilled with the marble texture `tex`, then the English goes centred in white with a dark rim"""
    x0, y0, x1, y1 = box
    rows = {}
    for y in range(y0, y1):
        xs = [x for x in range(x0, x1) if cv[y][x]]
        if xs and xs[-1] - xs[0] >= 20:
            rows[y] = (xs[0], xs[-1])
    top, bot = min(rows), max(rows)
    ix0, ix1 = rows[(top + bot) // 2][0] + 3, rows[(top + bot) // 2][1] - 3
    for y in range(top + 3, bot - 2):
        a, b = rows[y]
        for x in range(max(a + 3, ix0), min(b - 2, ix1 + 1)):
            cv[y][x] = tex[(y - top) % len(tex)][(x - ix0) % len(tex[0])]
    ink = max((i for i in range(1, 16)), key=lambda i: sum(pal[i]))
    shade = min((i for i in range(1, 16)), key=lambda i: sum(pal[i]))
    w = width(s) - 2
    assert w <= ix1 - ix0 + 1, f'{s!r} is {w} px, room {ix1 - ix0 + 1}'
    text(cv, (ix0 + ix1 + 1 - w) // 2, (top + bot) // 2 - 8, s, ink, shade)


def icon_map(rom_jp, k, pal, cv, at):
    """the English text icon k drawn in an overlay where the JP icon k sits at `at`: index pairs from the JP one"""
    jp = gfx_icons.get(rom_jp, k)

    def pairs(x0, y0):
        m, bad = {}, 0
        for y in range(16):
            for x in range(16):
                if jp[y][x]:
                    v = cv[y0 + y][x0 + x]
                    bad += m.setdefault(jp[y][x], v) != v or not v
        return bad, m
    spots = [(at[0] + dx, at[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)
             if 0 <= at[0] + dx and at[1] + dy + 16 <= 160]
    bad, m = min((pairs(*p) for p in spots), key=lambda t: t[0])
    assert bad == 0, f'icon {k} not found near {at}'
    en_rom = bytearray(rom_jp)
    gfx_icons.icons(en_rom)
    en = gfx_icons.get(en_rom, k)
    missing = {v for r in en for v in r if v and v not in m}
    assert not missing, f'icon {k}: colours {missing} not in the JP icon'
    return [[m[v] if v else 0 for v in r] for r in en]


def put(cv, px, at, keep0=True):
    x0, y0 = at
    for y, r in enumerate(px):
        for x, v in enumerate(r):
            if v or not keep0:
                cv[y0 + y][x0 + x] = v


def grab(cv, box):
    x0, y0, x1, y1 = box
    return [r[x0:x1] for r in cv[y0:y1]]


def bar(pal, cv, y0, x_end, parts, room=240):
    """reletter a green caption bar (rows y0..y0+15, left edge at x 0, right border ending at x_end): clear it to
    its plain green, then lay out parts (str = VWF text, list = a pixel block) from x 1, then grow or shrink the
    bar so its right border sits 3 px after the last part, ending at most at x `room`"""
    rows = [r[:] for r in cv[y0:y0 + 16]]
    def plain(r):   # the commonest green of a row (text and icons are not green)
        gs = [v for v in r[4:x_end - 4] if v and pal[v][1] > pal[v][0] + 24 and pal[v][1] > pal[v][2] + 24]
        return max(set(gs), key=gs.count) if gs else None
    green = [plain(r) for r in rows]
    main = max(set(g for g in green if g), key=green.count)
    green = [g if g and green.count(g) >= 3 else (r[x_end - 4] if r[x_end - 4] else main)
             for g, r in zip(green, rows)]
    edge = [r[x_end - 3:x_end] for r in rows]           # the right border columns
    ink = max((i for i in range(1, 16)), key=lambda i: sum(pal[i]))
    shade = min((i for i in range(1, 16)), key=lambda i: sum(pal[i]))
    for y in range(16):
        cv[y0 + y][3:240] = [green[y]] * 237
    x = 2
    for p in parts:
        if isinstance(p, str):
            x = text(cv, x, y0, p, ink, shade)
        else:
            put(cv, p, (x, y0 + (16 - len(p)) // 2))
            x += len(p[0])
    end = x + 3
    assert end + 3 <= room, f'bar at y {y0} needs {end + 3} px, room {room}'
    for y in range(16):
        cv[y0 + y][end:end + 3] = edge[y]
        cv[y0 + y][end + 3:240] = [0] * (237 - end)


def captions(rom, en):
    """D635A0: [AT]50で攻撃 / [木3]でダメージを30軽減; D635B8: [木]人物符は[木1]魑尼で1貫通 能力を得る"""
    _, pal, cv = load(rom, 0xD635A0)
    sword = grab(cv, (2, 0, 22, 16))
    tree = grab(cv, (6, 144, 24, 160))
    bar(pal, cv, 0, 88, [sword, 'Hits for 50'], room=92)   # a text window covers x >= 94 on that page
    bar(pal, cv, 144, 152, [tree, ' cuts damage by 30'])
    en[0xD635A0] = (pal, cv)
    _, pal, cv = load(rom, 0xD635B8)
    wd = icon_map(rom, 11, pal, cv, (1, 144))
    tree1 = grab(cv, (70, 144, 88, 160))
    bar(pal, cv, 144, 240, [wd, 'Characters get 1Prce at ', tree1, ' Mani'])
    en[0xD635B8] = (pal, cv)


def main():
    global FONT
    rom = (ROOT / 'rom' / 'base.gba').read_bytes()
    FONT = vwf.load_font(rom)
    en = {}
    epal, ecv = panel(rom, en)
    for e in HIGHLIGHTS:
        pal, cv = rebuild_highlights(rom, e, (epal, ecv))
        for box, s in BUBBLES.get(e, []):
            bubble(pal, cv, box, s, plate_texture(cv))
        en[e] = (pal, cv)
    captions(rom, en)
    for e, (pal, cv) in en.items():
        save(cv, pal, e)
        print(f'{e:06X}.png')


if __name__ == '__main__':
    main()
