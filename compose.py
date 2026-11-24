#!/usr/bin/env python3
"""Render "The World in One Day: Tuesday 24 November 2026" as a one-page
newspaper front page, 1024 x 1024 PNG.

Usage:
    python3 compose.py [output-path]

Without an argument the image is written to ./entry.png in the current
directory. The render is deterministic: fixed layout, fixed fonts, no
clocks, no randomness, no network access.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ layout
W = H = 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN            # 952
COL_GAP = 24
COL_W = (CONTENT_W - COL_GAP) // 2    # 464
LEFT_X = MARGIN
RIGHT_X = MARGIN + COL_W + COL_GAP    # 524
MID_X = MARGIN + COL_W + COL_GAP // 2  # 512, centre rule

PAPER = (247, 243, 233)
INK = (22, 19, 14)
SOFT = (96, 88, 74)
RED = (163, 22, 33)
NAVY = (17, 33, 55)
NAVY_LINE = (110, 140, 175)
WHITE = (250, 248, 242)

NOTO = "/usr/share/fonts/truetype/noto"
DEJAVU = "/usr/share/fonts/truetype/dejavu"


def load_font(filename, size, fallback=None):
    path = os.path.join(NOTO, filename)
    if not os.path.exists(path) and fallback:
        path = os.path.join(DEJAVU, fallback)
    return ImageFont.truetype(path, size)


def serif_display(size):
    return load_font("NotoSerifDisplay-Black.ttf", size, "DejaVuSerif-Bold.ttf")


def serif_black(size):
    return load_font("NotoSerif-Black.ttf", size, "DejaVuSerif-Bold.ttf")


def serif_xbold(size):
    return load_font("NotoSerif-ExtraBold.ttf", size, "DejaVuSerif-Bold.ttf")


def serif_bold(size):
    return load_font("NotoSerif-Bold.ttf", size, "DejaVuSerif-Bold.ttf")


def serif(size):
    return load_font("NotoSerif-Regular.ttf", size, "DejaVuSerif.ttf")


def serif_italic(size):
    return load_font("NotoSerif-Italic.ttf", size, "DejaVuSerif-Italic.ttf")


def sans_bold(size):
    return load_font("NotoSansDisplay-Bold.ttf", size, "DejaVuSans-Bold.ttf")


def sans(size):
    return load_font("NotoSans-Regular.ttf", size, "DejaVuSans.ttf")


# ------------------------------------------------------------------ helpers
def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, s, max_w, max_lines, start_size, make_font, min_size=22):
    """Largest size (<= start_size) whose wrap fits within max_lines."""
    size = start_size
    while size > min_size:
        fnt = make_font(size)
        lines = wrap(draw, s, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size * 1.13
        size -= 1
    fnt = make_font(min_size)
    return fnt, wrap(draw, s, fnt, max_w), min_size * 1.13


def spaced_center(draw, cx, y, s, fnt, spacing, fill):
    """Draw letterspaced text centred on cx; returns its total width."""
    widths = [text_w(draw, ch, fnt) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + spacing
    return total


def rule(draw, y, weight=1, fill=INK, x0=MARGIN, x1=W - MARGIN):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


def kicker(draw, x, y, s, fill=RED, size=15):
    fnt = sans_bold(size)
    spaced = " ".join(list(s.replace(" ", "\u00a0")))
    draw.text((x, y), s, font=fnt, fill=fill)
    return y + size + 6


def headline_block(draw, x, y, s, max_w, max_lines, start_size, make_font=serif_xbold):
    fnt, lines, lh = fit_headline(draw, s, max_w, max_lines, start_size, make_font)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=INK)
        y += lh
    return y


# ------------------------------------------------------------------ drawing
def draw_masthead(draw):
    # Eyebrow line above the nameplate.
    spaced_center(draw, W // 2, 18, "THE DAY'S WORLD NEWS · ON ONE PAGE",
                  sans_bold(14), 2, SOFT)
    rule(draw, 44, 3)
    rule(draw, 51, 1)

    # Nameplate, shrunk until it fits the measure.
    title = "THE WORLD IN ONE DAY"
    size = 92
    while size > 40:
        fnt = serif_display(size)
        if text_w(draw, title, fnt) + 2 * (len(title) - 1) <= CONTENT_W:
            break
        size -= 2
    spaced_center(draw, W // 2, 56, title, fnt, 2, INK)

    # Date band: solid black strip carrying the day in white.
    band_y0, band_y1 = 156, 206
    draw.rectangle([MARGIN, band_y0, W - MARGIN, band_y1], fill=INK)
    date_fnt = sans_bold(31)
    spaced_center(draw, W // 2, band_y0 + 8, "TUESDAY 24 NOVEMBER 2026",
                  date_fnt, 5, WHITE)
    return band_y1


def draw_lead(draw, y):
    kicker(draw, MARGIN, y, "LEAD STORY — WAR AT SEA")
    y += 30
    y = headline_block(
        draw, MARGIN, y,
        "Ukraine sinks a Russian warship off Libya in a sea-drone attack",
        CONTENT_W, 2, 56)
    y += 4
    deck_fnt = serif_italic(22)
    for line in wrap(draw,
                     "Kyiv's reach widens beyond Europe as its naval drones "
                     "strike a Russian warship off the Libyan coast.",
                     deck_fnt, CONTENT_W):
        draw.text((MARGIN, y), line, font=deck_fnt, fill=(52, 47, 38))
        y += 28
    y += 10

    # Left: the story in short. Right: a schematic panel of the strike.
    bullets_x = MARGIN
    bullets_w = 528
    draw.text((bullets_x, y), "THE STORY IN SHORT", font=sans_bold(15), fill=RED)
    by = y + 26
    bullet_fnt = serif(21)
    for item in ("Ukrainian sea drones sink a Russian warship",
                 "The strike lands off the coast of Libya",
                 "Kyiv's reach now extends beyond Europe"):
        draw.ellipse([bullets_x, by + 8, bullets_x + 7, by + 15], fill=RED)
        for line in wrap(draw, item, bullet_fnt, bullets_w - 20):
            draw.text((bullets_x + 18, by), line, font=bullet_fnt, fill=INK)
            by += 29
        by += 3

    panel = [588, y - 6, W - MARGIN, y + 104]
    draw.rectangle(panel, fill=NAVY)
    draw.text((panel[0] + 16, panel[1] + 12), "THE MEDITERRANEAN STRIKE",
              font=sans_bold(15), fill=WHITE)
    # Dotted route from Ukraine to the burst off Libya.
    x0, y0 = panel[0] + 52, panel[1] + 88
    x1, y1 = panel[0] + 322, panel[1] + 58
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        px = x0 + (x1 - x0) * t
        py = y0 + (y1 - y0) * t - math.sin(t * math.pi) * 16
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=NAVY_LINE)
    draw.ellipse([x0 - 5, y0 - 5, x0 + 5, y0 + 5], fill=WHITE)
    draw.text((x0 - 26, y0 - 30), "UKRAINE", font=sans_bold(13), fill=WHITE)
    # Starburst at the strike point.
    cx, cy = x1 + 14, y1
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = 17 if i % 2 == 0 else 7
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=(224, 84, 60))
    draw.text((cx - 20, cy + 22), "LIBYA", font=sans_bold(13), fill=WHITE)
    draw.text((panel[0] + 16, panel[1] + 36), "WARSHIP SUNK",
              font=sans_bold(13), fill=(224, 120, 95))
    # Waves along the panel foot.
    for wx in range(panel[0] + 18, panel[0] + 210, 32):
        draw.arc([wx, panel[3] - 20, wx + 22, panel[3] - 6],
                 start=180, end=360, fill=NAVY_LINE, width=2)
    return panel[3] + 16


def story(draw, x, y, kick, head, max_lines=3):
    kicker(draw, x, y, kick)
    return headline_block(draw, x, y + 21, head, COL_W, max_lines, 29)


def draw_secondary(draw, y):
    rule(draw, y, 2)
    y += 10
    top = y
    # Left column.
    ly = story(draw, LEFT_X, top, "WAR IN UKRAINE",
               "Russian strikes kill at least 15 in the Kyiv region",
               max_lines=2)
    ly += 8
    rule(draw, ly, 1, x0=LEFT_X, x1=LEFT_X + COL_W)
    ly += 10
    ly = story(draw, LEFT_X, ly, "NATO · SPACE DEFENCE",
               "NATO vows space defence amid reports Russia may launch a "
               "nuclear space weapon within weeks",
               max_lines=3)
    # Right column.
    ry = story(draw, RIGHT_X, top, "TECH & BUSINESS",
               "Nvidia reinstates Jensen Huang as CEO after Trump's "
               "intervention",
               max_lines=3)
    ry += 8
    rule(draw, ry, 1, x0=RIGHT_X, x1=RIGHT_X + COL_W)
    ry += 10
    ry = story(draw, RIGHT_X, ry, "UNITED STATES",
               "US Democrats clinch their biggest House majority in decades",
               max_lines=2)
    # Centre rule between the columns.
    draw.line([MID_X, top, MID_X, max(ly, ry)], fill=(178, 168, 148), width=1)
    return max(ly, ry) + 12


def draw_briefs(draw, y):
    rule(draw, y, 2)
    y += 10
    # Section header with flanking rules.
    hdr = "AROUND THE WORLD — IN BRIEF"
    hdr_fnt = sans_bold(16)
    hw = text_w(draw, hdr, hdr_fnt) + 3 * (len(hdr) - 1)
    draw.line([MARGIN, y + 9, W // 2 - hw / 2 - 14, y + 9], fill=INK, width=1)
    draw.line([W // 2 + hw / 2 + 14, y + 9, W - MARGIN, y + 9], fill=INK, width=1)
    spaced_center(draw, W // 2, y, hdr, hdr_fnt, 3, INK)
    y += 28

    items = [
        ("UNITED NATIONS",
         "UN chief calls for a global AI risk-management framework "
         "within a year"),
        ("SPORT",
         "US confirmed as a host of the 2031 Women's World Cup"),
        ("JAPAN",
         "Japan holds a second consular meeting with a reporter "
         "detained by Russia"),
        ("INDONESIA",
         "Indonesia's Prabowo names his vice-presidential picks"),
    ]
    brief_fnt = serif_bold(19)
    row_h = 66
    for row in range(2):
        for col in range(2):
            tag, head = items[row * 2 + col]
            x = LEFT_X if col == 0 else RIGHT_X
            draw.rectangle([x, y + 3, x + 8, y + 11], fill=RED)
            draw.text((x + 16, y - 2), tag, font=sans_bold(12), fill=RED)
            ly = y + 14
            for line in wrap(draw, head, brief_fnt, COL_W - 16):
                draw.text((x + 16, ly), line, font=brief_fnt, fill=INK)
                ly += 22
        y += row_h
    draw.line([MID_X, y - 2 * row_h, MID_X, y], fill=(178, 168, 148), width=1)
    return y


def draw_ticker(draw):
    band_y0 = H - 30
    draw.rectangle([0, band_y0, W, H], fill=INK)
    items = ("UN FOOD AGENCY WARNS WARS PUT FOOD AID FOR 7.3M MORE PEOPLE "
             "AT RISK  ·  GTA VI HACKER ARION KURTAJ SENTENCED TO 7 YEARS "
             "IN LONDON")
    fnt = sans_bold(13)
    while text_w(draw, items, fnt) > W - 40 and fnt.size > 9:
        fnt = sans_bold(fnt.size - 1)
    tw = text_w(draw, items, fnt)
    draw.text(((W - tw) / 2, band_y0 + 8), items, font=fnt, fill=WHITE)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(),
                                                            "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    y = draw_masthead(draw)
    y = draw_lead(draw, y + 18)
    y = draw_secondary(draw, y)
    draw_briefs(draw, y)
    draw_ticker(draw)

    img.save(out, format="PNG")
    size = os.path.getsize(out)
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}, {size} bytes")


if __name__ == "__main__":
    main()
