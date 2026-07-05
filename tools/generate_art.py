# =============================================================
# generate_art.py — programmatic art assets for the personal site.
#
# Purpose:  generate the designed image asset used by the site,
#           reproducibly (fixed seed), so the art can be regenerated or
#           re-tinted by editing constants below and re-running.
# Input:    none (pure noise field)
# Output:   ../assets/art-contours.svg  (topographic contour art,
#           transparent bg, used behind the contact banner)
#
# Run from anywhere:  python personal-site/tools/generate_art.py
# Deps: numpy, scipy, matplotlib.
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


if __name__ == "__main__":
    make_contours()
    size_kb = (ASSETS / "art-contours.svg").stat().st_size / 1024
    print(f"art-contours.svg: {size_kb:,.0f} KB")
