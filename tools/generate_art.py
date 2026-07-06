# =============================================================
# generate_art.py — programmatic art assets for the personal site.
#
# Purpose:  generate the designed image assets used by the site,
#           reproducibly (fixed seed), so they can be regenerated or
#           re-tinted by editing constants below and re-running.
# Input:    none (noise field + text)
# Output:   ../assets/art-contours.svg  (topographic contour art,
#           transparent bg, used behind the contact banner)
#           ../assets/og-card.png       (1200x630 social-share card:
#           name, positioning wedge, AB mark; Windows system fonts)
#
# Run from anywhere:  python personal-site/tools/generate_art.py
# Deps: numpy, scipy, matplotlib, Pillow.
# =============================================================
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless — no display server needed
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

# Site palette (keep in sync with styles.css tokens)
PERI = "#7089ba"
TEAL = "#57b3a1"
AMBER = "#e2b04a"

SEED = 42  # fixed seed → identical art on every run


def make_contours() -> None:
    """Topographic contour lines from smoothed noise — 'terrain of the data'.

    Smoothed Gaussian noise gives organic elevation; matplotlib draws only
    the contour lines (no fill) in the three site accents at low alpha, on a
    transparent background, exported as SVG so it scales crisply.
    """
    rng = np.random.default_rng(SEED)
    # wide field: matches the contact banner's aspect (roughly 3:1)
    elevation = gaussian_filter(rng.standard_normal((260, 780)), sigma=30)

    fig = plt.figure(figsize=(15.6, 5.2), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    # cycle the palette across levels; thin drafting-pen lines
    ax.contour(
        elevation,
        levels=14,
        colors=[PERI, TEAL, AMBER],
        linewidths=0.7,
        alpha=0.32,  # alpha baked into the asset — used as a background layer
    )
    fig.savefig(ASSETS / "art-contours.svg", transparent=True)
    plt.close(fig)


def make_og_card() -> None:
    """1200x630 social-share card in the blueprint language.

    Black canvas, dashed periwinkle frame, AB drafting mark, name in a
    heavy grotesque, the positioning wedge as mono annotations. Uses
    Windows system fonts (Arial Black + Consolas) so no font files ship.
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1200, 630
    PERI_RGB = (112, 137, 186)
    AMBER_RGB = (226, 176, 74)
    TEAL_RGB = (87, 179, 161)
    STEEL = (128, 128, 128)
    GRAPHITE = (77, 77, 77)
    PAPER = (255, 255, 255)

    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)

    def dashed_line(p0, p1, color, dash=12, gap=8, width=2):
        import math
        (ax, ay), (bx, by) = p0, p1
        length = math.hypot(bx - ax, by - ay) or 1.0
        n = int(length // (dash + gap)) + 1
        for i in range(n):
            t0 = (i * (dash + gap)) / length
            t1 = min((i * (dash + gap) + dash) / length, 1.0)
            if t0 >= 1.0:
                break
            d.line([(ax + (bx - ax) * t0, ay + (by - ay) * t0),
                    (ax + (bx - ax) * t1, ay + (by - ay) * t1)],
                   fill=color, width=width)

    # dashed frame
    m = 28
    dashed_line((m, m), (W - m, m), PERI_RGB)
    dashed_line((m, H - m), (W - m, H - m), PERI_RGB)
    dashed_line((m, m), (m, H - m), PERI_RGB)
    dashed_line((W - m, m), (W - m, H - m), PERI_RGB)

    fonts = Path(r"C:\Windows\Fonts")
    black = ImageFont.truetype(str(fonts / "ariblk.ttf"), 96)
    mono26 = ImageFont.truetype(str(fonts / "consola.ttf"), 26)
    mono20 = ImageFont.truetype(str(fonts / "consola.ttf"), 20)
    mark_f = ImageFont.truetype(str(fonts / "ariblk.ttf"), 30)

    # AB drafting mark
    mx, my, ms = 72, 64, 66
    dashed_line((mx, my), (mx + ms, my), PERI_RGB, dash=7, gap=5, width=2)
    dashed_line((mx, my + ms), (mx + ms, my + ms), PERI_RGB, dash=7, gap=5, width=2)
    dashed_line((mx, my), (mx, my + ms), PERI_RGB, dash=7, gap=5, width=2)
    dashed_line((mx + ms, my), (mx + ms, my + ms), PERI_RGB, dash=7, gap=5, width=2)
    bb = d.textbbox((0, 0), "AB", font=mark_f)
    d.text((mx + (ms - bb[2] + bb[0]) / 2, my + (ms - bb[3] + bb[1]) / 2 - 2),
           "AB", font=mark_f, fill=PAPER)

    # name
    d.text((70, 190), "ANASTASIA", font=black, fill=PAPER)
    d.text((70, 292), "BOGACHEVA", font=black, fill=PAPER)

    # wedge lines
    d.text((72, 452), "ANALYTICS ENGINEER — RISK, FRAUD & PAYMENTS DATA",
           font=mono26, fill=PERI_RGB)
    d.text((72, 496), "DATA THAT SURVIVES AUDITS · AAAANASTASIA.GITHUB.IO",
           font=mono20, fill=STEEL)

    # accent squares, one per system color
    for i, c in enumerate([PERI_RGB, TEAL_RGB, AMBER_RGB]):
        d.rectangle([W - 150 + i * 34, 72, W - 150 + i * 34 + 18, 90], outline=c, width=2)

    # corner annotation + stipple
    d.text((W - 320, H - 66), "FIG. 00 — CARD · SCALE 1:1", font=mono20, fill=GRAPHITE)
    rng = np.random.default_rng(SEED)
    for _ in range(26):
        x, y = rng.uniform(60, W - 60), rng.uniform(60, H - 60)
        if 150 < y < 540 and x < 950:
            continue  # keep the text zone clean
        d.point((x, y), fill=(255, 255, 255))

    img.save(ASSETS / "og-card.png", "PNG", optimize=True)


if __name__ == "__main__":
    make_contours()
    make_og_card()
    for name in ("art-contours.svg", "og-card.png"):
        size_kb = (ASSETS / name).stat().st_size / 1024
        print(f"{name}: {size_kb:,.0f} KB")
