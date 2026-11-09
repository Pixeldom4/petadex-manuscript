#!/usr/bin/env python3
"""Recolour the figure SVGs in ../figure-svgs to the PETadex colour palette.

Originals are never modified. Recoloured copies go into two parallel folders,
each mirroring the figure-svgs layout:

    color-palette/svgs/1a.plastics-production.svg          (vector source)
    color-palette/pngs/1a.plastics-production.png          (rendered figure)
    ...
    color-palette/svgs/figure-composites/petadex-figure-2-composite.svg
    color-palette/pngs/figure-composites/petadex-figure-2-composite.png

PNGs are rendered with rsvg-convert (Homebrew librsvg) on a white background,
PNG_WIDTH px wide = 600 DPI at the 160 mm Nature Communications text width.

Palette: petadex-color-palette.png / petadex-color-palette.json (same folder).

How it works
  * Vector colours: every #rrggbb in the SVG is looked up in a per-figure map.
    The map is keyed on the old hex, so a colour the original reused across
    panels (e.g. Fig. 2's Logan green) stays consistently reused.
    Unmapped colours (neutral greys, black, white) are left as they are.
  * "Family" entries recolour a shade or tint of an anchor colour, keeping its
    lightness offset from the anchor. That preserves bottle shading in Fig. 1B
    and the pale clade backgrounds in Fig. 2A.
  * Embedded PNGs (Fig. 2A protein cartoons, Fig. 2D ribbon gradient) are
    recoloured per pixel with the same rules.

Usage:  python3 color-palette/apply-palette.py        (from the repo root)
"""
import base64
import colorsys
import io
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "figure-svgs"
SVG_OUT = HERE / "svgs"
PNG_OUT = HERE / "pngs"
PNG_WIDTH, PNG_DPI = 3780, 600

# ---------------------------------------------------------------- palette ---
P = dict(
    red="#D43844", green="#70BA4B", blue="#5776F7",                     # primary
    yellow="#EFC233", teal="#437A76", orange="#E07251",                 # secondary
    purple="#680070", brown="#7A4028",                                  # brown: not used
    rose_l="#BE7C7E", rose_d="#491214",                                 # accents
    lilac_l="#C399C6", lilac_d="#340038",
    peri_l="#9AADFA", peri_d="#2C3B7C",
    cream_l="#F9E7AD", cream_d="#B39226",
    sage_l="#D5E5CC", sage_d="#4B6040",
    salmon_l="#ECAA97", salmon_d="#A02B10",
    slate_l="#8EAFAD", slate_d="#223D3B",
    taupe_l="#AF8C7E", taupe_d="#32170B",
)
DARK = {P[k].upper(): P[v] for k, v in [
    ("blue", "peri_d"), ("red", "rose_d"), ("orange", "salmon_d"), ("green", "sage_d"),
    ("purple", "lilac_d"), ("teal", "slate_d"), ("yellow", "cream_d"),
    ("lilac_l", "lilac_d"),
]}
# Neutrals taken from the Fig. 2B mock-up in petadex-color-palette.png
INK, BOX, BAR, OFFTARGET, RULE = "#000000", "#F3F3F3", "#D9D9D9", "#777777", "#E2E2E2"


# ------------------------------------------------------------ colour math ---
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb2hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(min(1, max(0, c)) * 255)) for c in rgb)


def dark_partner(tgt):
    """Shades of a palette colour run toward its dark accent partner."""
    return DARK.get(tgt.upper(), "#000000")


def family_rgb(l, src, tgt):
    """Colour at lightness `l` (array) in the family of `tgt`, given that `src`
    is the anchor of the old family. Tints (lighter than src) mix tgt with white
    by the same fraction; shades mix tgt toward its dark partner."""
    ls = colorsys.rgb_to_hls(*hex2rgb(src))[1]
    T = np.array(hex2rgb(tgt))
    D = np.array(hex2rgb(dark_partner(tgt)))
    l = np.asarray(l, dtype=np.float64)[..., None]
    up = np.clip((l - ls) / max(1 - ls, 1e-6), 0, 1)
    dn = np.clip((ls - l) / max(ls, 1e-6), 0, 1)
    light = T + (1 - T) * up
    dark = T + (D - T) * np.clip(dn * 1.6, 0, 1)   # reach the partner by ~40 % below the anchor
    return np.where(l >= ls, light, dark)


def family(hexcol, src, tgt):
    l = colorsys.rgb_to_hls(*hex2rgb(hexcol))[1]
    return rgb2hex(family_rgb(np.array(l), src, tgt))


def fam(src, tgt, *members):
    """Map entries for an anchor and its shades/tints."""
    m = {src: tgt}
    m.update({c: family(c, src, tgt) for c in members})
    return m


# ------------------------------------------------------------- Figure 1 ----
FIG1 = {}
# Plastics / PET: every blue in 1A and 1B, anchored on the PET blue of 1B
FIG1.update(fam("#2374C5", P["blue"],
                "#7DB3E8", "#A4CAEE", "#5097E0", "#4B95DF", "#247ACD", "#1E64AA",
                "#154474", "#1B5998", "#2A5FA0", "#D2E3F5", "#8AB4E0"))
FIG1.update({
    # 1A carbon treemap: light/dark accent pairs (fill / label)
    "#7DE8A1": P["sage_l"],   "#1F3A29": P["sage_d"],     # Plants
    "#F0C5A6": P["peri_d"],   "#3A2C22": "#FFFFFF",       # Fungi (white label on navy)
    "#ECDE97": P["cream_l"],  "#C9A227": P["cream_d"],    # Archaea
    "#7CD9DE": P["teal"],     "#2FA3AD": P["teal"],       # Protists (box + outside label)
    "#C59BED": P["lilac_l"],  "#2E2338": P["lilac_d"],    # Bacteria
    "#F2B3B4": P["salmon_l"], "#E04848": P["red"],        # Animal
    # 1B reaction
    "#591B98": P["purple"],  "#A15EE3": P["lilac_l"],     # MHET
    "#DDB23C": P["yellow"],                               # IsPETase cut sites
    "#DD3C3C": P["red"],
})
FIG1.update(fam("#1FAF4E", P["green"], "#24CA5B", "#5A9E3E"))   # Biomass

# ------------------------------------------------------------- Figure 2 ----
# Fig. 2A catalytic classes: old label colour -> palette colour.
# The classes sit in a 1-2 / 3-4 / 5-6 grid of structures AND in a 1..6 stack
# beside the tree, so no two neighbours in either layout get similar colours
# (red/orange, blue/navy, navy/purple are the near pairs to keep apart).
CLASS = {
    "#214E8C": P["peri_d"],  # 1 Ser-His-Asp triad (navy)
    "#8C212A": P["red"],     # 2 Ser-Lys type serine hydrolases
    "#D95412": P["green"],   # 3 N-terminal Thr
    "#278637": P["blue"],    # 4 Acid-base and aspartyl
    "#442786": P["orange"],  # 5 Metal-dependent
    "#7B2B82": P["purple"],  # 6 Heme enzymes
}
CLASS_TINTS = {  # pale clade backgrounds behind the tree, per class
    "#214E8C": ["#C4D6ED", "#D4E1F2", "#E4ECF6", "#F0F2F8"],
    "#8C212A": ["#F2D4D7", "#F6E4E5"],
    "#D95412": ["#FBDBCB"],
    "#278637": ["#D6F0DB", "#E5F5E8"],
    "#442786": ["#DED6F0", "#EAE5F5"],
    "#7B2B82": ["#ECD8EE", "#F3E6F4"],
}
# Structure annotation (3D cartoons + legend): old -> new
ANNOT = {
    "#1F9E89": P["teal"],     # plastic (spheres)
    "#E0A526": P["yellow"],   # secondary
    "#E8559A": P["lilac_l"],  # catalytic
}

FIG2 = {}
for src, tgt in CLASS.items():
    FIG2.update(fam(src, tgt, *CLASS_TINTS[src]))
FIG2.update(ANNOT)
FIG2.update({
    # 2A substrate columns
    "#275CA0": P["blue"],      # PET
    "#9A6FD4": P["lilac_l"],   # PBAT
    "#CC490B": P["orange"],    # PLA
    "#F0C95E": P["yellow"],    # PUR
    "#23873D": P["peri_d"],    # PBS
    "#8FBF5F": P["green"],     # PHA
    "#7A1F2B": P["red"],       # PEF
    "#8C6D46": P["peri_l"],    # PC
    "#40B6C5": P["teal"],      # PA
    "#E8559E": P["purple"],    # PE
    # 2B-2D dataset colours (as in the palette mock-up of 2B)
    "#5E689E": P["blue"], "#5F699E": P["blue"], "#0054D2": P["blue"],   # PETadex-PAZy / Domain
    "#BBBFD9": P["peri_l"],                                             # Domain tint
    "#9D5E91": P["green"],  "#D5B9D0": P["sage_l"],  "#7B5F9D": P["purple"],  # nr / PAZy+NR / Family
    "#679A79": P["red"], "#72A09C": P["red"],                           # Logan / Enzyme
    "#C1D6CA": P["salmon_l"],            # Enzyme shape fill (2C) / Logan singleton box (2D)
    "#7FA98D": P["rose_l"],              # Logan singleton label text (darker, for legibility)
    # Protein sits above Enzyme (red) in 2C, so it must not be red/orange
    "#E1595B": P["purple"], "#AC493D": P["purple"], "#E6BCB5": P["lilac_l"],  # Protein
    "#CBA945": P["cream_d"], "#E7D8AA": P["cream_l"],                   # Superfamily
    "#B6693D": P["orange"],
    # ink, boxes and bars -> mock-up neutrals
    "#5F3928": INK, "#805340": INK, "#80543F": INK,
    "#AC7F56": OFFTARGET, "#C8B388": BAR, "#F3E9E5": BOX,
    "#E5D9CD": RULE, "#E2E1DC": RULE,
    # unused <pattern> defs left in the Fig. 2 composite
    "#4F8FE8": P["blue"], "#6FB7E8": P["peri_l"], "#E74C4C": P["red"],
})


# ------------------------------------------------------------- Figure 3 ----
# The Fig. 3 panels (matplotlib) are already drawn in palette colours: red
# #D43844 (stated / clusters), yellow #EFC233 (inferred), teal #437A76
# (BioSamples) and the cream -> red -> dark-rose map ramp. Nothing to remap,
# and the 3B heatmap raster must NOT go through the Fig. 2 raster passes.
FIG3 = {}
NO_RASTER_PASS = (FIG3,)


# ---------------------------------------------------------- raster passes ---
def rgb_to_hls_np(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    l = (mx + mn) / 2
    d = mx - mn
    s = np.where(d == 0, 0, d / np.where(l < 0.5, mx + mn, 2 - mx - mn + 1e-12))
    dd = np.where(d == 0, 1, d)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) / 6
    h = np.where(d == 0, 0, h)
    return h, l, s


def hls_to_rgb_np(h, l, s):
    def f(n):
        k = (n + h * 12) % 12
        a = s * np.minimum(l, 1 - l)
        return l - a * np.clip(np.minimum(k - 3, 9 - k), -1, 1)
    return np.stack([f(0), f(8), f(4)], -1)


def hue_of(hexcol):
    return colorsys.rgb_to_hls(*hex2rgb(hexcol))[0]


def hue_dist(h, h0):
    d = np.abs(h - h0)
    return np.minimum(d, 1 - d) * 360


def recolor_protein(img):
    """Fig. 2A cartoon: recolour the class hue and the annotation hues."""
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255
    rgb, alpha = a[..., :3], a[..., 3]
    h, l, s = rgb_to_hls_np(rgb)
    vis = (alpha > 0) & (s > 0.25) & (l > 0.08) & (l < 0.92)
    # dominant hue of the cartoon decides which class this image is
    hist, edges = np.histogram(h[vis], bins=72, range=(0, 1))
    hdom = (edges[hist.argmax()] + edges[hist.argmax() + 1]) / 2
    cls = min(CLASS, key=lambda c: hue_dist(np.array(hdom), hue_of(c)))
    rules = [(hdom, cls, CLASS[cls], 12)] + [(hue_of(k), k, v, 9) for k, v in ANNOT.items()]
    out = rgb.copy()
    claimed = np.zeros(h.shape, bool)
    for h0, src, tgt, w in rules:
        d = hue_dist(h, h0)
        wt = np.clip(1 - (d - w) / 6, 0, 1) * np.clip(s / 0.15, 0, 1)   # soft edges
        wt[claimed] = 0
        if not wt.any():
            continue
        out = out * (1 - wt[..., None]) + family_rgb(l, src, tgt) * wt[..., None]
        claimed |= wt > 0.5
    res = np.concatenate([out, alpha[..., None]], -1)
    return Image.fromarray((np.clip(res, 0, 1) * 255).round().astype(np.uint8), "RGBA"), cls


def recolor_gradient(img, a_old, b_old, a_new, b_new):
    """Fig. 2D ribbon: pixels lie on a line a_old -> b_old; remap to a_new -> b_new."""
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255
    rgb = a[..., :3]
    A, B = np.array(hex2rgb(a_old)), np.array(hex2rgb(b_old))
    A2, B2 = np.array(hex2rgb(a_new)), np.array(hex2rgb(b_new))
    t = np.clip(((rgb - A) @ (B - A)) / ((B - A) @ (B - A)), 0, 1)[..., None]
    resid = rgb - (A + t * (B - A))          # keep any dither noise
    lin = lambda c: c ** 2.2                 # blend in linear light: no muddy midpoint
    mixed = (lin(A2) + t * (lin(B2) - lin(A2))) ** (1 / 2.2)
    a[..., :3] = np.clip(mixed + resid, 0, 1)
    return Image.fromarray((a * 255).round().astype(np.uint8), "RGBA")


def is_ribbon(img):
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255
    rgb = a[..., :3][a[..., 3] > 0]
    A, B = np.array(hex2rgb("#679A79")), np.array(hex2rgb("#9D5E91"))
    t = np.clip(((rgb - A) @ (B - A)) / ((B - A) @ (B - A)), 0, 1)[..., None]
    return len(rgb) and np.abs(rgb - (A + t * (B - A))).max() < 0.05


def recolor_images(text, log):
    def sub(m):
        mime, data = m.group(1), m.group(2)
        img = Image.open(io.BytesIO(base64.b64decode(data)))
        if is_ribbon(img):
            new, what = recolor_gradient(img, "#679A79", "#9D5E91", FIG2["#679A79"], FIG2["#9D5E91"]), "ribbon"
        else:
            new, cls = recolor_protein(img)
            what = f"protein, class {cls}"
        buf = io.BytesIO()
        new.save(buf, "PNG", optimize=True)
        log.append(f"    image {img.size[0]}x{img.size[1]}: {what}")
        return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()
    return re.sub(r"data:(image/png);base64,([A-Za-z0-9+/=\s]+)", sub, text)


# ------------------------------------------------------------------ driver --
JOBS = [
    ("1a.plastics-production.svg", FIG1),
    ("1b.enzymatic-solution.svg", FIG1),
    ("figure-composites/petadex-figure-1-composite.svg", FIG1),
    ("2a.petadex-pazy.svg", FIG2),
    ("2b.search-pipeline.svg", FIG2),
    ("2c.hierarchical-clustering.svg", FIG2),
    ("2d.logan-contribution.svg", FIG2),
    ("figure-composites/petadex-figure-2-composite.svg", FIG2),
    ("3a_coverage.svg", FIG3),
    ("3b_map.svg", FIG3),
    ("3c_profiles.svg", FIG3),
    ("figure-composites/petadex-figure-3-composite.svg", FIG3),
]
# One A4 portrait PDF page per composite (vector), each figure scaled to the full
# page width and centred vertically
PDF = HERE / "petadex-figure-composites.pdf"
PDF_PAGES = [j for j, _ in JOBS if j.startswith("figure-composites/")]
PAGE_W, PAGE_H = 210.0, 297.0  # mm, A4 portrait


# Element-level fixes, applied before the hex map, for places where one old hex
# needs two different new colours (e.g. a label that sits inside its own box).
OVERRIDES = [
    # Fig. 1A: "4 Gt" sits inside the now-teal Protists box -> white
    ('fill="#2fa3ad">4 Gt</text>', 'fill="#ffffff">4 Gt</text>'),
]


def main():
    # the Fig. 3 composite is generated from its panels; rebuild it first
    subprocess.run(["python3", "-I", str(SRC / "figure-composites" / "build-figure-3-composite.py")],
                   check=True)
    for rel, cmap in JOBS:
        text = (SRC / rel).read_text()
        for old, new in OVERRIDES:
            text = text.replace(old, new)
        log, hits = [], {}

        def sub(m):
            old = m.group(0).upper()
            if old in cmap:
                hits[old] = hits.get(old, 0) + 1
                return cmap[old].lower()
            return m.group(0)
        text = re.sub(r"#[0-9a-fA-F]{6}\b", sub, text)
        if not any(cmap is m for m in NO_RASTER_PASS):
            text = recolor_images(text, log)
        # Inkscape export of a copy goes to its twin in pngs/, never ../figures/
        png = PNG_OUT / Path(rel).with_suffix(".png")
        svg = SVG_OUT / rel
        rel_png = Path("../" * len(Path(rel).parts)) / "pngs" / Path(rel).with_suffix(".png")
        text = re.sub(r'inkscape:export-filename="[^"]*"',
                      f'inkscape:export-filename="{rel_png.as_posix()}"', text)
        svg.parent.mkdir(parents=True, exist_ok=True)
        svg.write_text(text)
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["rsvg-convert", "--unlimited", "-b", "white", "-w", str(PNG_WIDTH),
                        str(svg), "-o", str(png)], check=True)
        Image.open(png).save(png, dpi=(PNG_DPI, PNG_DPI), optimize=True)
        print(f"{rel}: {sum(hits.values())} colour refs in {len(hits)} colours -> svg + png")
        print("\n".join(log))

    # Three-page PDF of the recoloured composites: A4 pages, figure at full width
    with tempfile.TemporaryDirectory() as tmp:
        pages = []
        for i, rel in enumerate(PDF_PAGES, 1):
            page = Path(tmp) / f"page-{i}.svg"
            page.write_text(a4_page(SVG_OUT / rel))
            pages.append(str(page))
        subprocess.run(["rsvg-convert", "--unlimited", "-f", "pdf", "-o", str(PDF)] + pages,
                       check=True)
    print(f"{PDF.name}: {len(PDF_PAGES)} A4 pages")


def a4_page(svg_path):
    """Nest a figure SVG inside an A4 page, scaled to the full page width."""
    text = svg_path.read_text()
    text = re.sub(r"<\?xml[^>]*\?>", "", text, count=1)
    root = re.search(r"<svg\b[^>]*>", text)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', root.group(0)).group(1).replace(",", " ").split()]
    h = PAGE_W * vb[3] / vb[2]
    y = (PAGE_H - h) / 2
    tag = re.sub(r'\s(?:width|height|x|y)="[^"]*"', "", root.group(0))
    tag = tag[:-1].rstrip("/") + f' x="0" y="{y:.3f}" width="{PAGE_W}" height="{h:.3f}">'
    body = text[:root.start()] + tag + text[root.end():]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm" '
            f'viewBox="0 0 {PAGE_W} {PAGE_H}">\n'
            f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="#ffffff"/>\n{body}\n</svg>\n')


if __name__ == "__main__":
    main()
