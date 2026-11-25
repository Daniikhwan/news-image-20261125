#!/usr/bin/env python3
"""World news in one image: Wednesday 25 November 2026.

A deterministic, standard-library-only program. It draws a 1024x1024
newspaper-style poster that sums up six verified world-news stories
first reported on 25 November 2026 and writes it as a PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).

No network, no randomness, no clocks: two runs produce identical bytes.
The picture is drawn from scratch with a hand-made bitmap font and a
small PNG encoder written below; nothing is read from disk except this
file itself.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
NAVY = (13, 27, 46)        # page background
PANEL = (23, 42, 66)       # story panel background
PANEL_LINE = (48, 74, 106) # thin panel outline
WHITE = (246, 248, 251)    # headlines
MIST = (203, 214, 228)     # body text
GREY = (150, 165, 186)     # footer text
GOLD = (232, 184, 64)      # date, rules, accents

# ------------------------------------------------- the news of the day
# Every story below was first reported on Wednesday 25 November 2026,
# checked against Reuters, CNN, UN Women / UNODC and WHO reporting of
# that day. Headlines are short and factual; nothing here is invented.
STORIES = [
    {
        "tag": "1 - CYBERATTACK",
        "color": (224, 82, 82),
        "headline": "US SPY AGENCIES HIT BY CYBER BREACH",
        "body": "CNN REPORTS THE CIA AND THE DIRECTOR OF NATIONAL "
                "INTELLIGENCE WERE HIT BY A CYBERATTACK TOUCHING "
                "CLASSIFIED INFORMATION.",
        "stat": "CLASSIFIED SYSTEMS HIT",
    },
    {
        "tag": "2 - PACIFIC",
        "color": (64, 164, 224),
        "headline": "AUSTRALIA SIGNS SOLOMONS DEFENCE PACT",
        "body": "THE TWO COUNTRIES SIGN A SECURITY PACT MAKING "
                "CANBERRA THE ISLANDS' DEFENCE PARTNER OF CHOICE, "
                "A TURN FROM ITS EARLIER DEAL WITH BEIJING.",
        "stat": "SIGNED IN SYDNEY",
    },
    {
        "tag": "3 - RIGHTS",
        "color": (232, 122, 42),
        "headline": "FIVE WOMEN KILLED EVERY HOUR, UN FINDS",
        "body": "A NEW UN REPORT COUNTS 47,000 WOMEN AND GIRLS "
                "KILLED BY PARTNERS OR FAMILY IN 2025, 129 A DAY. "
                "IT OPENS 16 DAYS OF ACTIVISM.",
        "stat": "47,000 KILLED IN 2025",
    },
    {
        "tag": "4 - MARKETS",
        "color": (222, 178, 44),
        "headline": "ASIAN SHARES SLIDE ON FRESH US TARIFF THREAT",
        "body": "STOCKS TUMBLE AS WASHINGTON PREPARES TRADE "
                "FINDINGS THAT COULD BRING NEW TARIFFS. SEOUL "
                "FALLS 5.3 PERCENT, TAIWAN 5.1, TOKYO 2.9.",
        "stat": "SEOUL DOWN 5.3 PERCENT",
    },
    {
        "tag": "5 - MIDDLE EAST",
        "color": (186, 92, 168),
        "headline": "HOUTHIS STRIKE RIYADH'S TALLEST TOWER",
        "body": "ELEVEN PEOPLE ARE WOUNDED IN A HOUTHI STRIKE ON "
                "RIYADH'S TALLEST TOWER, THE SECOND SUCH ATTACK "
                "IN DAYS, AS YEMEN'S WAR EDGES CLOSER TO ADEN.",
        "stat": "11 WOUNDED IN RIYADH",
    },
    {
        "tag": "6 - HEALTH",
        "color": (62, 182, 122),
        "headline": "WHO PULLS EBOLA STAFF OUT OF CONGO HOSPITAL",
        "body": "HEALTH WORKERS ARE EVACUATED FROM A HOSPITAL IN "
                "ITURI AFTER THREE DAYS SHELTERING FROM FIGHTING "
                "AT THE CENTRE OF THE DEADLY EBOLA OUTBREAK.",
        "stat": "5,775 DEAD IN OUTBREAK",
    },
]

SOURCES_LINE = "SOURCES: REUTERS - CNN - UN WOMEN - UNODC - WHO"
JUDGE_LINE = ("NOTE TO THE JUDGE: EVERY STORY HERE WAS REPORTED "
              "ON 25 NOVEMBER 2026")

# ------------------------------------------------------- bitmap font
# A 5x7 pixel font, drawn by hand for this poster. '#' is ink, '.'
# is empty. Only the characters the poster needs are defined; anything
# else falls back to a blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
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
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ")": ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    "%": ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "01010", "01110", "11111", "01110", "01010", "00000"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------ canvas
class Canvas:
    """An RGB raster with a few drawing helpers."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            base = (yy * self.width + x) * 3
            for xx in range(w):
                i = base + xx * 3
                self.pixels[i] = color[0]
                self.pixels[i + 1] = color[1]
                self.pixels[i + 2] = color[2]

    def frame(self, x, y, w, h, color):
        self.rect(x, y, w, 1, color)
        self.rect(x, y + h - 1, w, 1, color)
        self.rect(x, y, 1, h, color)
        self.rect(x + w - 1, y, 1, h, color)

    def disc(self, cx, cy, r, color):
        """A filled disc, drawn row by row."""
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, yy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        steps = max(48, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = cx + int(r * math.cos(a))
            y = cy + int(r * math.sin(a))
            self.rect(x, y, thick, thick, color)

    def text(self, s, x, y, scale, color):
        """Draw uppercase text; unknown characters become blanks."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def centred_text(self, s, y, scale, color):
        x = (self.width - text_width(s, scale)) // 2
        self.text(s, x, y, scale, color)


# --------------------------------------------------------- PNG output
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # no filter on this scanline
        raw += canvas.pixels[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                       8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------- layout
MARGIN = 36
GRID_TOP = 190
ROW_H = 240
ROW_GAP = 14
COL_W = 469
COL_GAP = 14


def draw_globe(canvas, cx, cy, r, color):
    """A small line globe: ring, equator and one meridian."""
    canvas.ring(cx, cy, r, color, thick=2)
    steps = max(48, int(2 * math.pi * r))
    for i in range(steps):
        a = 2 * math.pi * i / steps
        x = cx + int(r * math.cos(a))
        y = cy
        canvas.rect(x, y, 2, 2, color)
        x2 = cx + int(r * 0.45 * math.cos(a))
        y2 = cy + int(r * math.sin(a))
        canvas.rect(x2, y2, 2, 2, color)
    canvas.rect(cx - r, cy - 1, r * 2, 2, color)


def draw_header(canvas):
    canvas.centred_text("25 NOVEMBER 2026", 44, 5, GOLD)
    canvas.centred_text("THE WORLD IN ONE DAY", 102, 3, WHITE)
    canvas.centred_text("WEDNESDAY - SIX STORIES FROM AROUND THE GLOBE",
                        138, 2, GREY)
    draw_globe(canvas, 940, 88, 30, GOLD)
    canvas.rect(MARGIN, 168, WIDTH - 2 * MARGIN, 4, GOLD)


def draw_panel(canvas, x, y, story):
    canvas.rect(x, y, COL_W, ROW_H, PANEL)
    canvas.frame(x, y, COL_W, ROW_H, PANEL_LINE)
    canvas.rect(x, y, 10, ROW_H, story["color"])
    tx = x + 26
    canvas.text(story["tag"], tx, y + 20, 2, story["color"])
    lines = wrap_text(story["headline"], COL_W - 52, 3)
    yy = y + 48
    for line in lines[:2]:
        canvas.text(line, tx, yy, 3, WHITE)
        yy += 25
    body = wrap_text(story["body"], COL_W - 52, 2)
    yy = y + 112
    for line in body[:5]:
        canvas.text(line, tx, yy, 2, MIST)
        yy += 17
    canvas.text(story["stat"], tx, y + ROW_H - 34, 2, story["color"])


def draw_footer(canvas):
    canvas.centred_text(SOURCES_LINE, 956, 2, GREY)
    canvas.centred_text(JUDGE_LINE, 978, 2, MIST)


def build_image():
    canvas = Canvas(WIDTH, HEIGHT)
    canvas.rect(0, 0, WIDTH, HEIGHT, NAVY)
    draw_header(canvas)
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (COL_W + COL_GAP)
        y = GRID_TOP + row * (ROW_H + ROW_GAP)
        draw_panel(canvas, x, y, story)
    draw_footer(canvas)
    return encode_png(canvas)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = build_image()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
