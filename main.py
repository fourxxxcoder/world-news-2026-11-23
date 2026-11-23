#!/usr/bin/env python3
"""One-page broadsheet of the world news of Monday 23 November 2026.

Pure Python 3.13 standard library, no network, no randomness.
The picture is drawn on a flat RGB raster with a hand-made 5x7
bitmap typeface and written out with a small hand-rolled PNG
encoder, so the output is byte-identical on every run.

The poster is written to entry.png inside the output directory:
$MAKEFUN_OUTPUT_DIR when set, else /output, else ./out.
"""

import math
import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024


# ------------------------------------------------------------ PNG output

def _png_chunk(tag, payload):
    chunk = struct.pack(">I", len(payload)) + tag + payload
    chunk += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
    return chunk


def save_png(path, width, height, rgb):
    """Save an RGB byte buffer (row-major, top row first) as a PNG."""
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    stride = width * 3
    scan = bytearray()
    for y in range(height):
        scan.append(0)  # filter type 0 on every scanline
        scan += rgb[y * stride:(y + 1) * stride]
    data = b"\x89PNG\r\n\x1a\n"
    data += _png_chunk(b"IHDR", header)
    data += _png_chunk(b"IDAT", zlib.compress(bytes(scan), 9))
    data += _png_chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


# ------------------------------------------------------------ 5x7 typeface
# Every glyph is 7 rows of 5 bits; "1" marks a printed pixel.
# The face is all-caps, like a newspaper headline cut.

GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}


def measure(text, scale):
    """Width in pixels of a string at the given scale."""
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines no longer than max_chars."""
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            if line and len(line) + 1 + len(word) > max_chars:
                out.append(line)
                line = word
            elif line:
                line = line + " " + word
            else:
                line = word
        if line:
            out.append(line)
    return out


# ------------------------------------------------------------ the canvas

class Page:
    """A flat RGB raster with newspaper drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg) * (w * h)

    def dot(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def box(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t=2):
        self.box(x, y, w, t, color)
        self.box(x, y + h - t, w, t, color)
        self.box(x, y, t, h, color)
        self.box(x + w - t, y, t, h, color)

    def rule(self, x, y, w, color, t=1):
        self.box(x, y, w, t, color)

    def seg(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line with a square nib of thickness t."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.box(x0, y0, t, t, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d2 <= r * r:
                    self.dot(xx, yy, color)
                elif not fill and abs(d2 - r * r) <= r:
                    self.dot(xx, yy, color)

    def tri(self, x0, y0, x1, y1, x2, y2, color):
        lo_x = max(0, min(x0, x1, x2))
        hi_x = min(self.w - 1, max(x0, x1, x2))
        lo_y = max(0, min(y0, y1, y2))
        hi_y = min(self.h - 1, max(y0, y1, y2))
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if den == 0:
            return
        for yy in range(lo_y, hi_y + 1):
            for xx in range(lo_x, hi_x + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den
                if a >= 0 and b >= 0 and 1 - a - b >= 0:
                    self.dot(xx, yy, color)

    def say(self, x, y, text, color, scale=2):
        """Draw text (forced to upper case); unknown glyphs stay blank."""
        pen = x
        for ch in text.upper():
            glyph = GLYPHS.get(ch)
            if glyph is not None:
                for r in range(7):
                    bits = glyph[r]
                    for col in range(5):
                        if bits[col] == "1":
                            self.box(pen + col * scale, y + r * scale,
                                     scale, scale, color)
            pen += 6 * scale

    def say_centered(self, cx, y, text, color, scale=2):
        self.say(cx - measure(text, scale) // 2, y, text, color, scale)

    def para(self, x, y, text, color, scale, max_chars, leading):
        """Draw a wrapped paragraph; return the y just below it."""
        yy = y
        for line in wrap(text, max_chars):
            self.say(x, yy, line, color, scale)
            yy += leading
        return yy


# ------------------------------------------------------------ palette

PAPER = (247, 241, 227)    # warm newsprint
INK = (20, 33, 61)         # deep navy ink
NAVY = (20, 33, 61)
NAVY_SOFT = (31, 48, 84)
RED = (180, 35, 24)        # headline red
ORANGE = (214, 106, 24)
GOLD = (212, 160, 23)
SEA = (14, 74, 78)         # gulf water
SEA_LIGHT = (24, 102, 106)
SKY = (168, 208, 214)
CREAM = (247, 241, 227)
WHITE = (255, 255, 255)
GREY = (110, 110, 105)
DARK = (30, 30, 30)
GREEN = (38, 110, 58)
BLUE = (36, 84, 160)


# ------------------------------------------------------------ pictograms
# Each icon is drawn inside a square of side s whose top-left is (x, y).

def icon_tanker(p, x, y, s, sea, hull, accent):
    p.box(x, y + s * 3 // 5, s, s * 2 // 5, sea)
    p.box(x + s // 10, y + s // 4, s * 4 // 5, s // 3, hull)
    p.box(x + s // 5, y + s // 10, s // 5, s // 5, accent)
    p.box(x + s // 2, y + s // 10, s // 5, s // 5, accent)
    p.seg(x + s // 10, y + s * 3 // 5, x + s // 2, y + s // 4, hull, 2)
    p.seg(x + s * 9 // 10, y + s * 3 // 5, x + s // 2, y + s // 4, hull, 2)
    for i in range(3):
        p.rule(x + i * s // 3, y + s * 7 // 8, s // 4, WHITE, 2)


def icon_burst(p, cx, cy, r, core, ray):
    for k in range(8):
        ang = k * math.pi / 4.0
        p.seg(int(cx + r * 0.45 * math.cos(ang)),
              int(cy + r * 0.45 * math.sin(ang)),
              int(cx + r * math.cos(ang)),
              int(cy + r * math.sin(ang)), ray, 3)
    p.disc(cx, cy, int(r * 0.45), core)
    p.disc(cx, cy, int(r * 0.22), WHITE)


def icon_globe(p, cx, cy, r, land, line):
    p.disc(cx, cy, r, land)
    p.disc(cx, cy, r, line, fill=False)
    p.seg(cx - r, cy, cx + r, cy, line, 2)
    p.seg(cx, cy - r, cx, cy + r, line, 2)
    p.seg(cx - r // 2, cy - r, cx - r // 2, cy + r, line, 1)
    p.seg(cx + r // 2, cy - r, cx + r // 2, cy + r, line, 1)


def icon_flame(p, x, y, s, color):
    p.tri(x + s // 2, y, x + s, y + s * 2 // 3, x, y + s * 2 // 3, color)
    p.tri(x + s // 4, y + s // 3, x + s * 3 // 4, y + s // 3,
          x + s // 2, y + s, color)
    p.disc(x + s // 2, y + s * 2 // 3, s // 4, color)


def icon_deal(p, x, y, s, color):
    # two arrows passing each other: a trade agreement
    p.seg(x, y + s // 3, x + s * 2 // 3, y + s // 3, color, 3)
    p.tri(x + s * 2 // 3, y + s // 6, x + s, y + s // 3,
          x + s * 2 // 3, y + s // 2, color)
    p.seg(x + s, y + s * 2 // 3, x + s // 3, y + s * 2 // 3, color, 3)
    p.tri(x + s // 3, y + s // 2, x, y + s * 2 // 3,
          x + s // 3, y + s * 5 // 6, color)


def icon_cap(p, x, y, s, color):
    # mortarboard: flat board, band beneath, tassel
    p.tri(x, y + s // 3, x + s // 2, y, x + s, y + s // 3, color)
    p.box(x + s // 4, y + s // 3, s // 2, s // 3, color)
    p.seg(x + s, y + s // 3, x + s, y + s * 2 // 3, color, 2)
    p.disc(x + s, y + s * 2 // 3, s // 12, color)


def icon_talks(p, x, y, s, color):
    p.box(x, y, s * 3 // 5, s // 2, color)
    p.tri(x + s // 10, y + s // 2, x + s // 5, y + s * 3 // 4,
          x + s // 3, y + s // 2, color)
    p.box(x + s * 2 // 5, y + s // 3, s * 3 // 5, s // 2, color)
    p.tri(x + s * 7 // 10, y + s * 5 // 6, x + s * 4 // 5, y + s * 5 // 6,
          x + s * 4 // 5, y + s * 5 // 6 - s // 2, color)


def icon_factory(p, x, y, s, color, smoke):
    p.box(x, y + s // 2, s, s // 2, color)
    p.box(x + s // 10, y + s // 5, s // 6, s * 3 // 10, color)
    p.box(x + s // 2, y + s // 10, s // 6, s * 2 // 5, color)
    p.disc(x + s // 6, y + s // 8, s // 10, smoke)
    p.disc(x + s // 3, y, s // 12, smoke)


def icon_cricket(p, x, y, s, wood, ball):
    p.seg(x + s // 5, y + s, x + s * 4 // 5, y + s // 5, wood, 4)
    p.disc(x + s * 4 // 5, y + s // 5, s // 8, ball)
    p.disc(x + s // 5, y + s * 4 // 5, s // 10, ball)


def icon_boat(p, x, y, s, hull, wave):
    p.tri(x, y + s // 2, x + s, y + s // 2, x + s // 2, y + s * 3 // 4, hull)
    p.seg(x + s // 2, y, x + s // 2, y + s // 2, hull, 2)
    p.tri(x + s // 2, y, x + s * 5 // 6, y + s // 4, x + s // 2,
          y + s // 2, hull)
    for i in range(3):
        p.rule(x + i * s // 4, y + s * 7 // 8, s // 5, wave, 2)


# ------------------------------------------------------------ the poster

def build_page():
    p = Page(PAGE_W, PAGE_H, PAPER)
    p.frame(0, 0, PAGE_W, PAGE_H, NAVY, 6)

    # ---- masthead -------------------------------------------------------
    p.box(6, 6, PAGE_W - 12, 106, NAVY)
    p.say_centered(PAGE_W // 2, 20, "THE WORLD IN ONE DAY", CREAM, 5)
    p.say_centered(PAGE_W // 2, 64, "MONDAY 23 NOVEMBER 2026", GOLD, 3)
    p.rule(60, 96, PAGE_W - 120, GOLD, 2)

    # ---- coverage ticker -------------------------------------------------
    p.box(14, 120, PAGE_W - 28, 28, NAVY_SOFT)
    p.say_centered(PAGE_W // 2, 127,
                   "11 STORIES - 6 REGIONS - THE WHOLE DAY ON ONE PAGE",
                   CREAM, 2)

    # ---- hero: the Gulf war widens ---------------------------------------
    hx, hy, hw, hh = 14, 156, PAGE_W - 28, 262
    p.box(hx, hy, hw, hh, SEA)
    p.frame(hx, hy, hw, hh, NAVY, 3)
    sx, sy = hx + 16, hy + 40
    p.rule(sx, sy + 150, 280, SKY, 2)
    icon_tanker(p, sx + 30, sy + 95, 115, SEA_LIGHT, NAVY, ORANGE)
    icon_burst(p, sx + 240, sy + 55, 42, ORANGE, GOLD)
    icon_burst(p, sx + 150, sy + 25, 26, GOLD, WHITE)
    p.seg(sx + 250, sy + 10, sx + 285, sy + 90, WHITE, 2)
    p.seg(sx + 120, sy + 5, sx + 160, sy + 80, GOLD, 2)
    p.say(sx, hy + 14, "LEAD STORY - MIDDLE EAST", GOLD, 2)
    tx = hx + 330
    p.say(tx, hy + 24, "GULF WAR", WHITE, 6)
    p.say(tx, hy + 76, "WIDENS", WHITE, 6)
    p.rule(tx, hy + 128, 560, GOLD, 2)
    p.para(tx, hy + 144,
           "IRAN SAYS IT STRUCK U.S. AIR DEFENCES IN BAHRAIN; "
           "BAHRAIN SAYS THE ATTACKS WERE REPELLED. A HOUTHI "
           "MISSILE TARGETS SAUDI ARABIA, AND TANKERS ARE HIT "
           "IN THE STRAIT OF HORMUZ.",
           CREAM, 2, 52, 20)

    # ---- second row: climate and Ukraine ---------------------------------
    def panel(x, y, w, h, label, band, headline, body, icon):
        p.box(x, y, w, h, WHITE)
        p.frame(x, y, w, h, NAVY, 2)
        p.box(x, y, w, 30, band)
        p.say(x + 12, y + 8, label, WHITE, 2)
        icon(p, x + 14, y + 44, 44)
        p.say(x + 70, y + 48, headline, INK, 3)
        p.para(x + 14, y + 100, body, DARK, 2, 38, 19)

    panel(14, 426, 492, 172, "CLIMATE - ANTALYA", GREEN,
          "TALKS COLLAPSE",
          "COP31 ENDS WITH NO DEAL AS THE EU REJECTS A TEXT "
          "THAT NEVER NAMES FOSSIL FUELS.",
          lambda q, x, y, s: icon_globe(q, x + s // 2, y + s // 2,
                                        s // 2, (190, 220, 180), GREEN))
    panel(518, 426, 492, 172, "WAR IN UKRAINE", BLUE,
          "KYIV REGION HIT",
          "14 MISSING AFTER A RUSSIAN DRONE STRIKES A BLOCK "
          "OF FLATS. A RUSSIAN CARGO SHIP BURNS OFF FINLAND.",
          lambda q, x, y, s: icon_flame(q, x, y, s, ORANGE))

    # ---- grid: six more stories -------------------------------------------
    tiles = [
        ("TRADE", "EU AND INDONESIA SIGN TRADE DEAL",
         "98.5% OF TARIFFS GO AFTER 10 YEARS OF TALKS",
         lambda q, x, y, s: icon_deal(q, x, y, s, BLUE)),
        ("SOUTH KOREA", "MINISTER QUITS IN AI CHEATING SCANDAL",
         "SEOUL'S EDUCATION CHIEF RESIGNS",
         lambda q, x, y, s: icon_cap(q, x, y, s, NAVY)),
        ("NEPAL - INDIA", "NEPAL PM MEETS MODI IN DELHI",
         "BALENDRA SHAH ON A STATE VISIT, 22-23 NOV",
         lambda q, x, y, s: icon_talks(q, x, y, s, GREEN)),
        ("INDONESIA", "FACTORY FIRE IN INDONESIA",
         "DOZENS MISSING AS RESCUERS SEARCH THE RUINS",
         lambda q, x, y, s: icon_factory(q, x, y, s, RED, GREY)),
        ("CRICKET", "INDIA 720 FOR 9: RECORD TEST TOTAL",
         "INDIA DECLARE IN WELLINGTON V NEW ZEALAND",
         lambda q, x, y, s: icon_cricket(q, x, y, s, ORANGE, RED)),
        ("NIGERIA", "BOAT CAPSIZES IN NIGERIA",
         "AT LEAST 24 MOURNERS KILLED ON THE WAY TO A BURIAL",
         lambda q, x, y, s: icon_boat(q, x, y, s, NAVY, BLUE)),
    ]
    tw, th, gap = 328, 160, 8
    for i, (label, headline, body, icon) in enumerate(tiles):
        x = 14 + (i % 3) * (tw + gap)
        y = 606 + (i // 3) * (th + gap)
        p.box(x, y, tw, th, WHITE)
        p.frame(x, y, tw, th, NAVY, 2)
        p.rule(x, y + 30, tw, RED, 3)
        p.say(x + 12, y + 9, label, RED, 2)
        icon(p, x + 12, y + 42, 40)
        p.para(x + 62, y + 44, headline, INK, 2, 20, 17)
        p.para(x + 12, y + 98, body, DARK, 2, 25, 17)

    # ---- footer -------------------------------------------------------------
    p.box(6, 942, PAGE_W - 12, 76, NAVY)
    p.say_centered(PAGE_W // 2, 952,
                   "ALSO TODAY: THOUSANDS MARCH IN LISBON OVER LIVING COSTS",
                   CREAM, 2)
    p.say_centered(PAGE_W // 2, 974,
                   "SINGAPORE PM WONG LANDS IN AUSTRALIA FOR LEADERS' MEETING",
                   CREAM, 2)
    p.say_centered(PAGE_W // 2, 1000,
                   "COMPILED FROM WIRE REPORTS - 23 NOVEMBER 2026", GOLD, 1)
    return p


def pick_output_dir():
    for cand in (os.environ.get("MAKEFUN_OUTPUT_DIR"), "/output", "out"):
        if not cand:
            continue
        try:
            os.makedirs(cand, exist_ok=True)
            probe = os.path.join(cand, ".write-test")
            with open(probe, "w") as fh:
                fh.write("ok")
            os.remove(probe)
            return cand
        except OSError:
            continue
    return "out"


def main():
    page = build_page()
    out = pick_output_dir()
    path = os.path.join(out, "entry.png")
    save_png(path, PAGE_W, PAGE_H, bytes(page.buf))
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
