"""Draft of Figure 3 (metadata), version V1 "coverage first".

Every number below is copied from the Obsidian notes in PETadex/Projects/Metadata and cited per
block. The per-sample tables live on the analysis box, not here, so two panels are partial:
  B  basemap only; the point layer needs the stated BioSample lat_lon (feature store), NOT the
     geocoded sra_metadata / Logan biosample_geographical_location points (country centroids).
  D  shows correlation by weighting arm; the measured-vs-inferred hexbin needs the 6,473 pH pairs.
    Run: python3 figure3_metadata_v1.py   ->  figure3_metadata_v1.svg
"""
import json
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 7,
    "svg.fonttype": "none",  # keep text editable in Illustrator/Inkscape
    "axes.linewidth": 0.5,
    "axes.edgecolor": "#52514e",
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 0,
    "xtick.color": "#52514e",
    "ytick.color": "#0b0b0b",
})

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
RECORDED = "#b9b8b2"   # provenance fields: neutral
MEASURED = "#2a78d6"   # L2, stated by the submitter
INFERRED = "#eb6834"   # L4, taxonomy x BacDive
ENV = "#1baf7a"        # environmental profiles
HOST = "#b9b8b2"       # host / clinical / other profiles

MM = 1 / 25.4
fig = plt.figure(figsize=(180 * MM, 128 * MM))
gs = fig.add_gridspec(2, 2, left=0.19, right=0.985, top=0.91, bottom=0.10,
                      wspace=0.55, hspace=0.62, width_ratios=[1, 1.08])


def panel_label(row, letter, title, x):
    """Panel letter + title in figure coordinates, aligned per grid row; x = column left edge."""
    y = gs[row, 0].get_position(fig).y1 + 0.045
    fig.text(x, y, letter, fontsize=9, fontweight="bold", va="bottom", ha="left", color=INK)
    fig.text(x + 0.022, y, title, fontsize=7.5, fontweight="bold", va="bottom", ha="left", color=INK)


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------------------------
# A  Annotation coverage, ORF-weighted (denominator 307,155,746 Logan catalytic ORFs)
#    Source: BioSample Annotation Layer/00 Annotation Layer - Overview.md §2
# ---------------------------------------------------------------------------------------------
ax = fig.add_subplot(gs[0, 0])
cov = [
    ("BioSample resolved", 256_236_322, RECORDED),
    ("Environmental profile (cluster)", 251_857_584, RECORDED),
    ("Collection date", 145_751_250, RECORDED),
    ("Coordinates (lat/lon)", 98_337_577, RECORDED),
    ("Isolation source", 87_354_211, RECORDED),
    ("Temperature, measured", 6_431_531, MEASURED),
    ("pH, measured", 2_264_177, MEASURED),
    ("Temperature, inferred", 247_519_349, INFERRED),
    ("pH, inferred", 202_153_063, INFERRED),
]
N_ORF = 307_155_746
ys = [0, 1, 2, 3, 4, 5.6, 6.6, 8.2, 9.2]  # gaps separate the three groups
for (lab, n, c), y in zip(cov, ys):
    v = 100 * n / N_ORF
    ax.barh(y, v, height=0.72, color=c, edgecolor="none")
    ax.text(v + 1.2, y, f"{n / 1e6:.1f} M ({v:.1f}%)", va="center", ha="left", fontsize=6.2, color=INK2)
ax.set_yticks(ys, [c[0] for c in cov], fontsize=6.5)
ax.invert_yaxis()
ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100])
ax.spines["bottom"].set_bounds(0, 100)
ax.set_xlabel("PETadex-logan ORFs annotated (% of 307.2 M)", color=INK2)
clean(ax)
for y, txt, c in [(-0.95, "Recorded provenance", INK2), (4.85, "Measured at collection", MEASURED),
                  (7.45, "Inferred from taxonomy", INFERRED)]:
    ax.text(118, y, txt, ha="right", va="center", fontsize=6.3, fontstyle="italic", color=c)
ax.set_ylim(9.8, -1.5)
panel_label(0, "A", "Annotation coverage", 0.01)

# ---------------------------------------------------------------------------------------------
# B  Geographic origin (basemap; point layer pending)
#    Natural Earth 1:110m land via world-atlas@2 (topojson), Equal Earth projection
# ---------------------------------------------------------------------------------------------
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2


def equal_earth(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    t = math.asin(M * math.sin(phi))
    t2, t6 = t * t, t ** 6
    x = 2 * math.sqrt(3) * lam * math.cos(t) / (3 * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = t * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


topo = json.load(open("land-110m.json"))
(sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in arc:
        x += dx
        y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)


def ring(idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


ax = fig.add_subplot(gs[0, 1])
outline = [equal_earth(-180, la) for la in range(-90, 91)] + [equal_earth(180, la) for la in range(90, -91, -1)]
ax.add_patch(Polygon(outline, closed=True, facecolor="#f4f4f2", edgecolor=MUTED, lw=0.5))
for g in topo["objects"]["land"]["geometries"]:
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    for poly in polys:
        for r in poly:
            pts = [equal_earth(min(max(lo, -179.999), 179.999), la) for lo, la in ring(r)]
            ax.add_patch(Polygon(pts, closed=True, facecolor="#d9d8d3", edgecolor="none"))
ax.set_xlim(-2.75, 2.75)
ax.set_ylim(-1.36, 1.36)
ax.set_aspect("equal")
ax.axis("off")
ax.text(0, -0.05, "POINT LAYER PENDING\nstated BioSample lat_lon, 808,766 BioSamples\n(not geocoded country centroids)",
        ha="center", va="center", fontsize=6.3, color=INK2,
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=MUTED, lw=0.5, ls=(0, (2, 2))))
panel_label(0, "B", "Geographic origin of PETadex BioSamples", 0.53)

# ---------------------------------------------------------------------------------------------
# C  Profiles: the samples are clinical, the enzymes are environmental
#    Source: Metadata Profiles Experiment/02 Profiles - Results and Validation.md §1, §5
#    Left: share of the 2,744,599-BioSample universe. Right: share of the 14,455,359 profiled
#    90% clusters, by dominant profile. Only the profiles listed in the notes are shown; the
#    full cross-table is profile_summary.csv on the analysis box.
# ---------------------------------------------------------------------------------------------
ENV_PROFILES = {"soil", "other_environmental", "marine", "freshwater", "plant_associated"}
bios = [("human_other", 771_354), ("human_gut", 288_492), ("unprofilable", 266_122),
        ("animal_other", 255_782), ("human_respiratory", 176_170), ("other_environmental", 170_943),
        ("plant_associated", 136_030), ("food", 123_337), ("soil", 99_768), ("animal_gut", 67_787)]
clus = [("soil", 4_694_207), ("other_environmental", 2_581_412), ("marine", 1_221_889),
        ("freshwater", 1_201_201), ("plant_associated", 897_597), ("human_gut", 82_013)]
N_BIOS, N_CLUS = 2_744_599, 14_455_359

sub = gs[1, 0].subgridspec(1, 2, wspace=0.95)
axes_c = []
for k, (rows, n, head) in enumerate([(bios, N_BIOS, "BioSamples (n = 2.74 M)"),
                                     (clus, N_CLUS, "Sequence clusters (n = 14.46 M)")]):
    ax = fig.add_subplot(sub[0, k])
    axes_c.append(ax)
    for y, (name, cnt) in enumerate(rows):
        v = 100 * cnt / n
        ax.barh(y, v, height=0.72, color=ENV if name in ENV_PROFILES else HOST, edgecolor="none")
        ax.text(v + 1, y, f"{v:.1f}", va="center", ha="left", fontsize=6, color=INK2)
    ax.set_yticks(range(len(rows)), [r[0].replace("_", " ") for r in rows], fontsize=6.3)
    ax.set_ylim(9.6, -0.6)
    ax.set_xlim(0, 40)
    ax.set_xticks([0, 20, 40])
    ax.set_xlabel("Share (%)", color=INK2)
    ax.set_title(head, fontsize=6.5, color=INK, pad=4, loc="left")
    clean(ax)
panel_label(1, "C", "Samples are clinical, enzymes environmental", 0.01)
axes_c[1].text(0, 7.2, "environmental", color=ENV, fontsize=6.3, fontweight="bold")
axes_c[1].text(0, 8.2, "host / clinical / other", color=INK2, fontsize=6.3, fontweight="bold")

# ---------------------------------------------------------------------------------------------
# D  Inferred vs measured: correlation by weighting arm
#    pH: Weighted Bands/04 Results.md §4a (n = 6,473 BioSamples with measured pH + abundance label)
#    Temperature: Metadata - Catalogue.md §5 (n = 45,741 pairs; only two arms reported)
# ---------------------------------------------------------------------------------------------
ax = fig.add_subplot(gs[1, 1])
arms = ["abundance", "rank", "detection", "species"]
ph_r = {"abundance": 0.3434, "rank": 0.2044, "detection": 0.1475, "species": 0.1396}
t_r = {"abundance": 0.159, "species": 0.054}
for j, (axis_name, vals, n) in enumerate([("pH", ph_r, "6,473"), ("Temperature", t_r, "45,741")]):
    y0 = j * 5.4
    ax.text(-0.005, y0 - 0.95, f"{axis_name}  (n = {n})", fontsize=6.5, fontweight="bold", color=INK,
            transform=ax.get_yaxis_transform(), ha="right")
    for i, arm in enumerate(arms):
        y = y0 + i
        if arm in vals:
            v = vals[arm]
            ax.plot([0, v], [y, y], color=INFERRED, lw=1.2, alpha=0.35, solid_capstyle="round")
            ax.scatter(v, y, s=26, color=INFERRED if arm == "abundance" else "white",
                       edgecolor=INFERRED, lw=1.2, zorder=3)
            ax.text(v + 0.012, y, f"{v:.2f}", va="center", fontsize=6, color=INK2)
        else:
            ax.text(0.005, y, "not reported", va="center", fontsize=6, color=MUTED, fontstyle="italic")
ax.set_yticks([j * 5.4 + i for j in range(2) for i in range(4)], arms * 2, fontsize=6.3)
ax.set_ylim(8.9, -1.6)
ax.set_xlim(0, 0.42)
ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
ax.set_xlabel("Pearson r, inferred vs measured", color=INK2)
clean(ax)
ax.text(0.42, 8.55, "Ranks samples, not calibrated: every pH arm\nhas higher MAE than a constant pH 7.0",
        ha="right", va="bottom", fontsize=5.8, color=INK2, fontstyle="italic")
panel_label(1, "D", "Inferred conditions track measurements", 0.53)

fig.text(0.005, 0.005, "DRAFT V1 · numbers from Obsidian Metadata notes (2026-09-18 builds) · B and D partial",
         fontsize=5.5, color=MUTED)
fig.savefig("figure3_metadata_v1.svg")
fig.savefig("figure3_metadata_v1_preview.png", dpi=220)
