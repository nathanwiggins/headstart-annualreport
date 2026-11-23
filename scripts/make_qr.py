"""Branded QR code to the flipbook: ink dots, SUU-red finder rings, and the
SUU Thunderbird logo in the middle (error correction H, so the dots the logo
covers don't matter). Same design as the SPARC annual report's QR code.

    pip install segno pymupdf pillow
    python3 scripts/make_qr.py            # writes assets/qr-code.svg and .png

Pass --url to point it somewhere else.
"""
import argparse
import base64
import io
import math
from pathlib import Path

import pymupdf
import segno
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INK, RED, WHITE = "#161513", "#DB0000", "#ffffff"
QUIET = 4            # modules of white around the code
DOT_R = 0.43         # data dot radius, in modules
LOGO_W = 0.31        # logo width as a share of the code's width
KNOCKOUT = 0.82      # drop dots whose centers are this close (modules) to the logo
PNG_PX = 32          # PNG pixels per module


def num(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def rounded(x, y, w, h, r):
    """A rounded rectangle as one closed subpath."""
    return (f"M{num(x + r)},{num(y)}h{num(w - 2 * r)}a{num(r)},{num(r)} 0 0 1 {num(r)},{num(r)}"
            f"v{num(h - 2 * r)}a{num(r)},{num(r)} 0 0 1 {num(-r)},{num(r)}"
            f"h{num(-(w - 2 * r))}a{num(r)},{num(r)} 0 0 1 {num(-r)},{num(-r)}"
            f"v{num(-(h - 2 * r))}a{num(r)},{num(r)} 0 0 1 {num(r)},{num(-r)}z")


def dot(cx, cy, r):
    return f"M{num(cx - r)},{num(cy)}a{num(r)},{num(r)} 0 1 0 {num(2 * r)},0a{num(r)},{num(r)} 0 1 0 {num(-2 * r)},0z"


def make_svg(url, title):
    qr = segno.make(url, error="h", boost_error=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    size = n + 2 * QUIET

    finders = [(0, 0), (n - 7, 0), (0, n - 7)]                       # (col, row) of each 7x7 finder
    pos = segno.consts.ALIGNMENT_POS[qr.version - 2] if qr.version > 1 else ()  # table starts at version 2
    aligns = [(c, r) for r in pos for c in pos
              if not any(fc - 1 <= c <= fc + 7 and fr - 1 <= r <= fr + 7 for fc, fr in finders)]

    def is_pattern(c, r):
        return (any(fc <= c < fc + 7 and fr <= r < fr + 7 for fc, fr in finders)
                or any(abs(c - ac) <= 2 and abs(r - ar) <= 2 for ac, ar in aligns))

    # Logo: suu-logo.png trimmed to its edges, centered; its opaque pixels set the knockout.
    logo = Image.open(ROOT / "assets/suu-logo.png").convert("RGBA")
    logo = logo.crop(logo.getchannel("A").getbbox())
    lw = n * LOGO_W
    lh = lw * logo.height / logo.width
    lx, ly = size / 2 - lw / 2, size / 2 - lh / 2
    alpha = logo.getchannel("A")
    opaque = [(lx + (i + 0.5) / logo.width * lw, ly + (j + 0.5) / logo.height * lh)
              for j in range(0, logo.height, 2) for i in range(0, logo.width, 2)
              if alpha.getpixel((i, j)) > 128]

    def under_logo(cx, cy):
        if not (lx - 1 < cx < lx + lw + 1 and ly - 1 < cy < ly + lh + 1):
            return False
        return any(math.hypot(px - cx, py - cy) < KNOCKOUT for px, py in opaque)

    dots = []
    for r in range(n):
        for c in range(n):
            if matrix[r][c] and not is_pattern(c, r):
                cx, cy = c + QUIET + 0.5, r + QUIET + 0.5
                if not under_logo(cx, cy):
                    dots.append(dot(cx, cy, DOT_R))

    rings = "".join(rounded(c + QUIET, r + QUIET, 7, 7, 0.6) + rounded(c + QUIET + 1, r + QUIET + 1, 5, 5, 0.38)
                    for c, r in finders)
    eyes = "".join(rounded(c + QUIET + 2, r + QUIET + 2, 3, 3, 0.26) for c, r in finders)
    align_rings = "".join(rounded(c + QUIET - 2, r + QUIET - 2, 5, 5, 0.6) + rounded(c + QUIET - 1, r + QUIET - 1, 3, 3, 0.38)
                          for c, r in aligns)
    align_dots = "".join(dot(c + QUIET + 0.5, r + QUIET + 0.5, 0.5) for c, r in aligns)

    buf = io.BytesIO()
    logo.save(buf, "PNG", optimize=True)
    href = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {size} {size}" width="{size * 12}" height="{size * 12}" role="img" aria-label="QR code to the {title}">
<title>{title} · {url}</title>
<rect width="{size}" height="{size}" rx="1.6" fill="{WHITE}"/>
<path fill="{INK}" d="{''.join(dots)}"/>
<path fill="{RED}" fill-rule="evenodd" d="{rings}"/>
<path fill="{INK}" d="{eyes}"/>
"""
    if aligns:
        svg += f"""<path fill="{INK}" fill-rule="evenodd" d="{align_rings}"/>
<path fill="{RED}" d="{align_dots}"/>
"""
    svg += f"""<image x="{num(lx)}" y="{num(ly)}" width="{num(lw)}" height="{num(lh)}" href="{href}" xlink:href="{href}"/>
</svg>
"""
    return svg, size, qr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="https://nathanwiggins.github.io/headstart-annualreport/")
    ap.add_argument("--title", default="SUU Head Start Annual Report")
    ap.add_argument("--out", default=str(ROOT / "assets/qr-code"), help="output path without extension")
    args = ap.parse_args()

    svg, size, qr = make_svg(args.url, args.title)
    svg_path, png_path = Path(args.out + ".svg"), Path(args.out + ".png")
    svg_path.write_text(svg, encoding="utf-8")

    doc = pymupdf.open(svg_path)
    zoom = size * PNG_PX / doc[0].rect.width
    doc[0].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True).save(png_path)
    print(f"{args.url}  (version {qr.version}-{qr.error}, mask {qr.mask})\n  {svg_path}\n  {png_path}")


if __name__ == "__main__":
    main()
