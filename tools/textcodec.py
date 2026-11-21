"""textcodec.py: game text bytes <-> script text (the `jp` / `en` columns of script/*.tsv).

The game stores text as Shift-JIS (cp932) with ASCII control codes inline (docs/re/text.md). In script text:

    {rt}                line break                      {nl}      0A 0D, line break (card / tutorial text)
    {wc} {wk} {wd}      wait for key (+ clear)          {pp}      page clear (tutorial)
    {dc}                end of a staff-roll page        {name1}   01 00, player surname (story lines)
    {I000}              inline icon / card-type insert  {name2}   02 00, player given name
    {&x04} {&Sx0} ..    position / number formats       {xn} {yn} name codes in the 0xD64Bxx name lists (guess)
    [XX]                any other byte, kept as is (so decode -> encode is byte-exact)

Everything else is literal: Japanese and fullwidth characters, and printable ASCII other than { } [ ] \\. A cp932
character that doesn't re-encode to the same two bytes (NEC / IBM duplicates) stays as [XX][YY].

Note for English (phase 5/7): the game reads `rt`, `wc`.. wherever they appear, so literal English like "start"
must not reach the ROM as plain ASCII; the insert encoder and lint handle that once the font path is known.
"""
import re

CODE = re.compile(rb'rt|wc|wk|wd|dc|pp|xn|yn|I\d\d\d|&(?:[xyXz]\d\d|S[xyz]\d|N[XYy]\d)')
SPECIAL = {b'\n\r': 'nl', b'\x01\x00': 'name1', b'\x02\x00': 'name2'}
SPECIAL_ENC = {v: k for k, v in SPECIAL.items()}
TOKEN = re.compile(r'\{([^{}]+)\}|\[([0-9A-F]{2})\]')
ASCII_LIT = set(range(0x20, 0x7F)) - set(b'{}[]\\')


def is_lead(c):
    return 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC


def decode(b):
    """bytes -> script text"""
    out, i, n = [], 0, len(b)
    while i < n:
        c = b[i]
        two = b[i:i + 2]
        if two in SPECIAL:
            out.append('{%s}' % SPECIAL[two])
            i += 2
            continue
        if is_lead(c) and i + 1 < n:
            try:
                ch = two.decode('cp932')
                if ch.encode('cp932') == two:
                    out.append(ch)
                    i += 2
                    continue
            except UnicodeDecodeError:
                pass
            out.append('[%02X]' % c)
            i += 1
            continue
        m = CODE.match(b, i)
        if m:
            out.append('{%s}' % m.group().decode('ascii'))
            i = m.end()
            continue
        out.append(chr(c) if c in ASCII_LIT else '[%02X]' % c)
        i += 1
    return ''.join(out)


def encode(s):
    """script text -> bytes; raises ValueError on an unknown {code}"""
    out, pos = bytearray(), 0
    for m in TOKEN.finditer(s):
        out += _literal(s[pos:m.start()])
        if m.group(2):
            out.append(int(m.group(2), 16))
        else:
            name = m.group(1)
            if name in SPECIAL_ENC:
                out += SPECIAL_ENC[name]
            elif CODE.fullmatch(name.encode('ascii', 'replace')):
                out += name.encode('ascii')
            else:
                raise ValueError('unknown code {%s} in %r' % (name, s))
        pos = m.end()
    out += _literal(s[pos:])
    return bytes(out)


def _literal(s):
    for ch in '{}[]\\\t\n\r':
        if ch in s:
            raise ValueError('stray %r in %r (write bytes as [XX])' % (ch, s))
    return s.encode('cp932')
