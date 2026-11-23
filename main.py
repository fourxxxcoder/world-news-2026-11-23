#!/usr/bin/env python3
"""THE DAILY ORBIT — a one-image broadsheet of the world's day.

Draws a single 1024x1024 PNG front page that sums up the world news of
Monday 23 November 2026: a hero story (the COP31 collapse in Antalya)
plus a three-column gazette of sourced stories from six continents.

Pure Python 3.13 standard library: a hand-rolled framebuffer, a 5x7
bitmap typeface defined below, word-wrap and column-flow layout, and a
zlib/struct PNG writer. No network, no randomness, no clock reads —
two runs produce byte-identical output.

Run:  python3 main.py          (writes poster.png into /output)
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas

PAGE_W = 1024
PAGE_H = 1024

PAPER = (246, 240, 224)      # warm newsprint cream
INK = (26, 23, 18)           # near-black ink
CRIMSON = (163, 31, 22)      # accent red for kickers and rules
SLATE = (43, 58, 82)         # section-label blue-grey
FAINT = (112, 103, 88)       # footer grey-brown
RULE = (198, 187, 158)       # pale column rule


class Canvas:
    """A flat RGB framebuffer with rectangle and line primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def ring(self, cx, cy, r, color, thick=2):
        """Circle outline drawn by distance test in its bounding box."""
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= thick / 2.0:
                    self.px(xx, yy, color)


def save_png(canvas, path):
    """Minimal deterministic PNG writer (filter 0 rows, zlib level 9)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)

# ------------------------------------------------------------------ font
# A 5x7 bitmap typeface, drawn as string art: '#' is ink, '.' is paper.
# Every glyph is 7 rows of 5 columns; the pen advances 6 units per char.

GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("..##.", ".#...", "#....", "#....", "#....", ".#...", "..##."),
    ")": (".##..", "...#.", "....#", "....#", "....#", "...#.", ".##.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "%": (".#..#", "#...#", "....#", "...#.", "..#..", ".#...", "#...#"),
}

# Characters that reuse another glyph's shape.
ALIASES = {"–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
           "·": ".", "…": "."}


def glyph(ch):
    if ch in ALIASES:
        ch = ALIASES[ch]
    return GLYPHS.get(ch, GLYPHS["?"])


def text_w(s, scale):
    """Pixel width of a string: 5 ink columns + 1 space column per char."""
    return len(s) * 6 * scale - (scale if s else 0)


def draw_text(cv, x, y, s, scale, color, bold=False):
    """Draw one line of text with its top at y; returns the pen's end x."""
    pen = x
    extra = max(1, scale // 2) if bold else 0
    for ch in s:
        rows = glyph(ch)
        for gy, row in enumerate(rows):
            for gx, cell in enumerate(row):
                if cell == "#":
                    cv.rect(pen + gx * scale, y + gy * scale,
                            scale + extra, scale, color)
        pen += 6 * scale
    return pen


def wrap(s, scale, max_w):
    """Greedy word wrap against the fixed-pitch font metrics."""
    lines = []
    cur = ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, s, scale, color, max_w, leading, bold=False):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap(s, scale, max_w):
        draw_text(cv, x, y, line, scale, color, bold)
        y += 7 * scale + leading
    return y


def block_h(s, scale, max_w, leading):
    return len(wrap(s, scale, max_w)) * (7 * scale + leading)

# --------------------------------------------------------------- content
# Every story below was researched on the morning of 23 Nov 2026; the
# reporting behind each line is listed in SOURCES.md.

HERO_KICKER = "CLIMATE - ANTALYA, TURKEY"
HERO_HEADLINE = ("COP31 TALKS", "COLLAPSE")
HERO_SUBHEAD = "NO DEAL AS FOSSIL-FUEL WORDS VANISH FROM THE PACT"
HERO_BODY = (
    "After two weeks and record overtime, the UN climate summit ended "
    "without a deal on Sunday. The EU, Panama and island states "
    "refused a text that never mentions fossil fuels; oil states "
    "backed it."
)
HERO_STATS = (
    "194 DELEGATIONS AT THE TABLE",
    "LONGEST COP IN HISTORY",
    "FIRST BREAKDOWN SINCE 2009",
    "90+ NATIONS SIGN POWER PLEDGE",
)
HERO_QUOTE = '"DIFFICULT GEOPOLITICAL TIMES" - AUSTRALIA PM ALBANESE'

SECTIONS = (
    ("EUROPE AT WAR", (
        ("MISSILES CROSS INTO POLAND",
         "Warsaw says three Russian cruise missiles struck Polish "
         "soil; a drone strike leveled a Kyiv-region block, 14 "
         "missing."),
        ("SEA DRONES HIT RUSSIAN FLEET",
         "Suspected Ukrainian sea drones struck a warship at Benghazi "
         "and the Baltic base."),
    )),
    ("MIDDLE EAST", (
        ("IRAN STRIKE WOUNDS TWO IN BAHRAIN",
         "Houthi claims of hits on a Saudi refinery left six hurt; the "
         "US embassy warned its citizens."),
        ("ISRAEL UNITY TALKS END WITHOUT DEAL",
         "Likud and Eisenkot's Yashar broke off talks on forming a "
         "government."),
    )),
    ("AFRICA", (
        ("24 CIVILIANS KILLED IN SOUTH SUDAN",
         "An SPLA-IO attack left 24 dead in fresh violence, AFP "
         "reported."),
        ("WHO PLEADS FOR CALM IN CONGO",
         "Fighting near the Ebola zone is disrupting the response, "
         "the WHO chief warned."),
        ("DRONES STRIKE KHARTOUM",
         "Homes and a UN building were hit in Sudan's capital; revenge "
         "attacks killed 35 in Nigeria."),
    )),
    ("ASIA-PACIFIC", (
        ("FACTORY FIRE IN INDONESIA",
         "A candy factory blaze killed at least three; dozens of "
         "workers are missing."),
        ("QUAKE JOLTS NORTHERN JAPAN",
         "A preliminary magnitude 6.1 earthquake shook the north on "
         "Monday."),
    )),
    ("TECHNOLOGY", (
        ("UN TALKS ON LETHAL AI GO ON",
         "Nations agreed to keep negotiating rules for AI weapons "
         "systems."),
        ("US SEEKS NVIDIA ANSWERS",
         "Treasury wants compliance details over reported chip sales "
         "to China."),
    )),
    ("AMERICAS", (
        ("HELD AT SEATTLE AIRPORT",
         "A father and daughter were detained by ICE en route to a "
         "family baptism."),
        ("CARTEL BOSS CAPTURED",
         "Mexico seized FBI-most-wanted 'El Chapo Isidro'; Sinaloa "
         "firefights killed 11."),
        ("BOLSONARO STABLE IN CARE",
         "Brazil's ex-president is stable in intensive care in "
         "Brasilia."),
    )),
    ("SPORT", (
        ("LIVERPOOL 4-0 MAN UNITED",
         "Pochettino's debut nightmare: Yoro off in eight minutes, "
         "four goals at Anfield."),
    )),
)

# ---------------------------------------------------------------- layout

MARGIN = 44
INNER_W = PAGE_W - 2 * MARGIN
COL_W = 296
COL_XS = (44, 364, 684)
BODY_SCALE = 2
LINE_STEP = 7 * BODY_SCALE + 2
STORY_GAP = 4
SECTION_GAP = 10


def section_h(section):
    """Height of one section block: header, stories, trailing gap."""
    _name, stories = section
    h = 7 * BODY_SCALE + 10
    for head, blurb in stories:
        h += block_h(head, BODY_SCALE, COL_W, 1)
        h += block_h(blurb, BODY_SCALE, COL_W, 1)
        h += STORY_GAP
    return h + SECTION_GAP


def partition(sections):
    """Balance sections over three columns: each section, in editorial
    order, joins the currently shortest column."""
    cols = [[], [], []]
    heights = [0, 0, 0]
    for sec in sections:
        i = heights.index(min(heights))
        cols[i].append(sec)
        heights[i] += section_h(sec)
    return cols


def draw_section(cv, x, y, section):
    name, stories = section
    draw_text(cv, x, y, name, BODY_SCALE, SLATE, bold=True)
    y += 7 * BODY_SCALE + 4
    cv.hline(x, y, COL_W, CRIMSON, thick=2)
    y += 6
    for head, blurb in stories:
        y = draw_block(cv, x, y, head, BODY_SCALE, INK, COL_W, 1,
                       bold=True)
        y = draw_block(cv, x, y, blurb, BODY_SCALE, INK, COL_W, 1)
        y += STORY_GAP
    return y + SECTION_GAP


def masthead(cv, y):
    cv.hline(MARGIN, y, INNER_W, INK, thick=3)
    cv.hline(MARGIN, y + 5, INNER_W, INK, thick=1)
    y += 16
    name = "THE DAILY ORBIT"
    nx = (PAGE_W - text_w(name, 9)) // 2
    draw_text(cv, nx, y, name, 9, INK, bold=True)
    cv.ring(MARGIN + 12, y + 30, 9, CRIMSON, thick=2)
    cv.ring(PAGE_W - MARGIN - 12, y + 30, 9, CRIMSON, thick=2)
    y += 7 * 9 + 12
    left = "MONDAY 23 NOVEMBER 2026"
    mid = "ONE IMAGE - THE WHOLE DAY"
    right = "WORLD DESK - NO. 23"
    draw_text(cv, MARGIN, y, left, BODY_SCALE, INK, bold=True)
    draw_text(cv, (PAGE_W - text_w(mid, BODY_SCALE)) // 2, y, mid,
              BODY_SCALE, CRIMSON, bold=True)
    draw_text(cv, PAGE_W - MARGIN - text_w(right, BODY_SCALE), y, right,
              BODY_SCALE, INK, bold=True)
    y += 7 * BODY_SCALE + 10
    cv.hline(MARGIN, y, INNER_W, INK, thick=3)
    return y + 14


def hero(cv, y):
    draw_text(cv, MARGIN, y, HERO_KICKER, BODY_SCALE, CRIMSON, bold=True)
    tag = "THE DAY'S LEAD"
    draw_text(cv, PAGE_W - MARGIN - text_w(tag, BODY_SCALE), y, tag,
              BODY_SCALE, SLATE, bold=True)
    y += 7 * BODY_SCALE + 8
    for line in HERO_HEADLINE:
        draw_text(cv, MARGIN, y, line, 6, INK, bold=True)
        y += 7 * 6 + 4
    y += 2
    draw_text(cv, MARGIN, y, HERO_SUBHEAD, 3, INK, bold=True)
    y += 7 * 3 + 10
    y = draw_block(cv, MARGIN, y, HERO_BODY, BODY_SCALE, INK, INNER_W, 2)
    y += 6
    box_w = (INNER_W - 3 * 12) // 4
    for i, stat in enumerate(HERO_STATS):
        bx = MARGIN + i * (box_w + 12)
        cv.hline(bx, y, box_w, CRIMSON, thick=3)
        draw_block(cv, bx, y + 8, stat, BODY_SCALE, INK, box_w, 2,
                   bold=True)
    y += 8 + 2 * LINE_STEP + 10
    qx = PAGE_W - MARGIN - text_w(HERO_QUOTE, BODY_SCALE)
    draw_text(cv, qx, y, HERO_QUOTE, BODY_SCALE, SLATE)
    y += LINE_STEP + 8
    cv.hline(MARGIN, y, INNER_W, INK, thick=1)
    cv.hline(MARGIN, y + 3, INNER_W, INK, thick=3)
    return y + 16


def footer(cv, y, story_count):
    cv.hline(MARGIN, y, INNER_W, INK, thick=3)
    y += 10
    left = "%d STORIES - 6 CONTINENTS - ONE IMAGE" % story_count
    draw_text(cv, MARGIN, y, left, BODY_SCALE, FAINT, bold=True)
    right = "COMPILED 23 NOV 2026"
    draw_text(cv, PAGE_W - MARGIN - text_w(right, BODY_SCALE), y, right,
              BODY_SCALE, FAINT, bold=True)
    y += LINE_STEP
    src = "SOURCES: REUTERS, CNN, AFP, LE MONDE, WSJ, THE HINDU - SOURCES.MD"
    draw_text(cv, MARGIN, y, src, BODY_SCALE, FAINT)
    return y + LINE_STEP


def build():
    cv = Canvas(PAGE_W, PAGE_H, PAPER)
    y = masthead(cv, 16)
    y = hero(cv, y)
    cols = partition(SECTIONS)
    col_top = y
    bottom = col_top
    for i, col in enumerate(cols):
        cy = col_top
        for sec in col:
            cy = draw_section(cv, COL_XS[i], cy, sec)
        bottom = max(bottom, cy)
    for rx in (352, 672):
        cv.vline(rx, col_top, bottom - col_top - SECTION_GAP, RULE,
                 thick=1)
    story_count = 1 + sum(len(s[1]) for s in SECTIONS)
    footer(cv, PAGE_H - 52, story_count)
    if os.environ.get("ORBIT_DEBUG"):
        import sys
        heights = [sum(section_h(s) for s in c) for c in cols]
        print("columns:", heights, "bottom:", bottom, file=sys.stderr)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    save_png(build(), os.path.join(out_dir, "poster.png"))


if __name__ == "__main__":
    main()
