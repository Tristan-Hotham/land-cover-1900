"""Reddit collage (r/dataisbeautiful style): farmland in 1900 and 2023 on two Equal Earth maps, with labels on open sea,
and the long series of world cropland and grazing land. Run from the repo root or anywhere: python3 reddit/collage.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from figstyle import *

R = jload(f"{DATA}/results.json"); H, CH = R["hyde"], R["change"]
ml = np.nan_to_num(LW("maxln_cr")); den = np.where(ml > 0, ml, np.nan)
farm = {y: np.nan_to_num((np.nan_to_num(LW(f"cropland{y}")) + np.nan_to_num(LW(f"grazing{y}"))) / den) for y in YEARS}
HALO = [pe.withStroke(linewidth=4, foreground=BG)]
W_IN, H_IN, DPI = 12, 17.6, 220
fig = plt.figure(figsize=(W_IN, H_IN), facecolor=BG)
ext = (-12.3e6, 15.6e6, -6.2e6, 8.35e6)
mh = .335
fig.text(.04, .975, f"Farms covered {H['farm_1900_pct']:.0f}% of the world's ice-free land in 1900.", fontproperties=DISP, fontsize=26, color=FG, va="top")
fig.text(.04, .947, f"Today they cover {H['farm_2023_pct']:.0f}%.", fontproperties=DISP, fontsize=26, color="#B5562E", va="top")
fig.text(.04, .921, f"Cropland and grazing land (pasture and rangeland) as a share of the land, 1900 and 2023. Farmland grew by {H['farm_gain_km2'] / 1e6:.1f} million km²,\n"
         f"{H['farm_gain_vs_us']:.1f} times the area of the United States. Only Europe farms less land than in 1900.", fontproperties=SERP, fontsize=12.5, color=FG, va="top", linespacing=1.35)
maps = {}
for y, top in ((1900, .54), (2023, .205)):
    ax = fig.add_axes([0, top, 1, mh]); world(ax, lambda i: LAND, lw=.25, extent=ext)
    draw_raster(ax, share_rgba(farm[y], 2600, ext, cmap("farm")), ext)
    world(ax, lambda i: None, lw=.3, ec="#9C9480", z=3, extent=ext, fill=False)
    x, yy = ee(-122, -30)
    ax.text(x, yy, str(y), fontproperties=DISP, fontsize=46, color=FG, ha="center", va="center", zorder=6, path_effects=HALO)
    x, yy = ee(-122, -44)
    ax.text(x, yy, f"{H[f'farm_{y}_pct']:.0f}% of ice-free\nland farmed", fontsize=12, color=FG, ha="center", va="center", zorder=6, path_effects=HALO, linespacing=1.3)
    maps[y] = ax


def lab(ax, text, at, to, ha="center"):
    ax.annotate(text, ee(*at), ee(*to), fontsize=11, color=FG, ha=ha, va="center", zorder=7, path_effects=HALO, linespacing=1.25,
                arrowprops=dict(arrowstyle="-", color="#6B675E", lw=.9, shrinkA=8, shrinkB=1))


HS = CH["hotspots"]
p = lambda k, y: f"{HS[k][f'farm_{y}_pct']:.0f}%"
a = maps[1900]
lab(a, f"Western and central\nEurope: {p('europe_w', 1900)}", (8, 49), (-31, 50))
lab(a, f"US Midwest already\nploughed: {p('midwest', 1900)}", (-88, 42), (-48, 30))
lab(a, f"Brazilian Cerrado:\nopen savanna, {p('cerrado', 1900)}", (-48, -14), (-12, -24))
a = maps[2023]
lab(a, f"Cerrado: {p('cerrado', 2023)}", (-48, -14), (-14, -22))
lab(a, f"Sahel:\n{p('sahel', 1900)} to {p('sahel', 2023)}", (0, 13), (-36, 6))
lab(a, f"Western and central\nEurope: down to {p('europe_w', 2023)}", (8, 49), (-40, 50))
lab(a, f"Southeast Asia:\n{p('se_asia', 1900)} to {p('se_asia', 2023)}", (110, 5), (150, 10))
lab(a, f"Australia: {CH['top_farm_gain'][2]['v'] / 1e6:+.1f} million km²\nof farmland, mostly grazing", (135, -25), (98, -42))
# legend ramp
ax = fig.add_axes([.30, .183, .40, .010]); ax.imshow(np.linspace(0, 1, 256)[None, :], aspect="auto", cmap=cmap("farm"))
ax.set_xticks([0, 255]); ax.set_xticklabels(["1% of the land", "100%"], fontsize=10.5); ax.set_yticks([]); ax.tick_params(length=0)
for s in ax.spines.values(): s.set_visible(False)
fig.text(.5, .198, "Farmland (cropland plus grazing land), share of each 9 km square", fontsize=11, color=FG, ha="center")
# stacked series
S0 = R["series"]; yrs = np.array(S0["years"]); cr = np.array(S0["crop"]); gz = np.array(S0["graz"])
ax = fig.add_axes([.09, .078, .55, .066]); ax.set_facecolor(BG)
ax.stackplot(yrs, cr, gz, colors=[COL["crop"], COL["graz"]], alpha=.95)
for y in YEARS:
    for v in (H[f"crop_{y}_km2"], H[f"farm_{y}_km2"]):
        ax.plot([y], [v / 1e6], "o", ms=6, mfc=BG, mec=FG, mew=1.4, zorder=5)
ax.axvline(1900, color=MUT, lw=.8, ls=":"); ax.set_xlim(1700, 2025); ax.set_ylim(0, 55); ax.set_yticks([0, 25, 50])
ax.set_ylabel("million km²", fontsize=10); ax.tick_params(labelsize=10)
ax.text(1712, cr[0] / 2, "Cropland", fontsize=10.5, va="center"); ax.text(1712, cr[0] + gz[0] / 2 + 1.5, "Grazing land", fontsize=10.5, va="center")
fig.text(.09, .158, "World farmland, 1700 to today", fontproperties=SERB, fontsize=14, color=FG)
fig.text(.09, .148, "HYDE 3.2 world totals; dots are HYDE 3.3 for 1900 and 2023", fontsize=9.5, color=MUT)
# numbers panel
k = [(f"{H['crop_1900_km2'] / 1e6:.1f} to {H['crop_2023_km2'] / 1e6:.1f}", "million km² of cropland", COL["crop"]),
     (f"{H['graz_1900_km2'] / 1e6:.1f} to {H['graz_2023_km2'] / 1e6:.1f}", "million km² of grazing land", "#5F8A3A"),
     (f"{R['forest']['cleared_1900_pct']:.0f}% to {R['forest']['cleared_2023_pct']:.0f}%", "of the natural forest zone farmed", "#2F6B4F")]
for i, (big, small_, c) in enumerate(k):
    fig.text(.69, .152 - i * .030, big, fontproperties=DISP, fontsize=20, color=c, va="top")
    fig.text(.69, .134 - i * .030, small_, fontsize=10, color=FG, va="top")
fig.text(.04, .012, "Data: HYDE 3.3 baseline (Klein Goldewijk et al., Utrecht University, CC BY 4.0); HYDE 3.2 world series via Our World in Data; outlines Natural Earth.\n"
         "Ice-free land excludes Antarctica and the Greenland ice sheet. 1900 values are model estimates from historical statistics.\n"
         "Interactive map, paper and data: maps.tristanhotham.com/land-cover-1900",
         fontsize=9, color=MUT, linespacing=1.5)
fig.savefig(os.path.join(ROOT, "reddit", "world_farmland_1900_2023.png"), dpi=DPI, facecolor=BG)
print("collage saved")
