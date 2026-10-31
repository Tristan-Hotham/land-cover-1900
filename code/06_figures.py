"""Static figures: header.png (1200 x 630), blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png).
Maps are drawn from the HYDE 3.3 5 arc-minute grids and Natural Earth outlines in the Equal Earth projection, no web tiles."""
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
H, F, AN, CH = R["hyde"], R["forest"], R["anthromes"], R["change"]
REL = os.path.join(ROOT, "release"); os.makedirs(f"{REL}/blog", exist_ok=True); os.makedirs(f"{REL}/paper", exist_ok=True)

ml = np.nan_to_num(LW("maxln_cr")); fw = np.nan_to_num(LW("forest_wwf_cr")) > .5
den = np.where(ml > 0, ml, np.nan)
farm = {}
for y in YEARS:
    farm[y] = np.nan_to_num((np.nan_to_num(LW(f"cropland{y}")) + np.nan_to_num(LW(f"grazing{y}"))) / den)
dfarm = farm[2023] - farm[1900]
clr = {y: np.where(fw, np.nan_to_num((np.nan_to_num(LW(f"cropland{y}")) + np.nan_to_num(LW(f"pasture{y}")) + np.nan_to_num(LW(f"conv_rangeland{y}"))) / den), 0) for y in YEARS}
dclr = np.where(fw, clr[2023] - clr[1900], 0)


def outs(name):
    return [f"{REL}/blog/b_{name}.png", f"{REL}/paper/f_{name}.png"]


def legend(fig, items, y, ncol=4, x=.03, fs=10):
    h = [Patch(fc=c, ec="none", label=l) for l, c in items]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(x, y), ncol=ncol, frameon=False, fontsize=fs, handlelength=1.2,
               handleheight=1.0, columnspacing=1.3, labelspacing=.45)


def rampbar(fig, rect, colours, lo, hi, label):
    ax = fig.add_axes(rect); ax.imshow(np.linspace(0, 1, 256)[None, :], aspect="auto", cmap=mcolors.LinearSegmentedColormap.from_list("r", colours))
    ax.set_xticks([0, 255]); ax.set_xticklabels([lo, hi], fontsize=8.5); ax.set_yticks([]); ax.set_title(label, fontsize=9, loc="left", color=FG)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)


EXT = WORLD_EXT
# ---------- header 1200 x 630 ----------
fig = plt.figure(figsize=(6, 3.15), facecolor=BG)
ext = (-12.3e6, 15.6e6, -5.9e6, 8.3e6)
ax1 = fig.add_axes([.33, .50, .66, .48]); world(ax1, lambda i: LAND, lw=.12, extent=ext); draw_raster(ax1, share_rgba(farm[1900], 1100, ext, cmap("farm")), ext)
ax2 = fig.add_axes([.33, .01, .66, .48]); world(ax2, lambda i: LAND, lw=.12, extent=ext); draw_raster(ax2, share_rgba(farm[2023], 1100, ext, cmap("farm")), ext)
for ax, t in ((ax1, "1900"), (ax2, "2023")):
    ax.text(.02, .08, t, transform=ax.transAxes, fontproperties=DISP, fontsize=13, color=FG)
fig.text(.04, .88, "Desert,", fontproperties=DISP, fontsize=21, color="#C9921A", va="top")
fig.text(.04, .755, "forest,", fontproperties=DISP, fontsize=21, color="#2F6B4F", va="top")
fig.text(.04, .63, "ice", fontproperties=DISP, fontsize=21, color="#7FA8BC", va="top")
fig.text(.04, .45, f"Farms covered {H['farm_1900_pct']:.0f}% of the\nworld's ice-free land in\n1900. Today: {H['farm_2023_pct']:.0f}%.",
         fontproperties=SERP, fontsize=8.6, color=FG, va="top", linespacing=1.45)
fig.text(.04, .06, "maps.tristanhotham.com/land-cover-1900", fontsize=5.4, color=MUT)
save(fig, os.path.join(ROOT, "header.png"))

# ---------- 1. farmland 1900 and 2023 ----------
for out in outs("maps"):
    fig = plt.figure(figsize=(7.6, 8.2), facecolor=BG)
    for k, (y, top) in enumerate(((1900, .53), (2023, .10))):
        ax = fig.add_axes([0, top, 1, .43]); world(ax, lambda i: LAND, lw=.2); draw_raster(ax, share_rgba(farm[y], 2000, EXT, cmap("farm")))
        ax.text(.03, .1, str(y), transform=ax.transAxes, fontproperties=DISP, fontsize=22, color=FG)
        ax.text(.03, .03, f"{H[f'farm_{y}_pct']:.0f}% of ice-free land farmed", transform=ax.transAxes, fontsize=9, color=MUT)
    rampbar(fig, [.30, .055, .40, .016], RAMPS["farm"], "1%", "100%", "Cropland and grazing land, share of the land")
    fig.text(.03, .005, "HYDE 3.3 baseline (Klein Goldewijk et al.), 5 arc-minute grid. Antarctica not shown.", fontsize=7.5, color=MUT)
    save(fig, out)

# ---------- 2. change map ----------
LABS = [("cerrado", "Brazilian\nCerrado", (-25, -24)), ("se_asia", "Southeast\nAsia", (152, 10)), ("sahel", "Sahel", (-30, 9)),
        ("wheatbelt", "Australian\nwheat belt", (98, -38)), ("europe_w", "Europe:\nless farmland", (-30, 52)), ("east_us", "Eastern US:\nless farmland", (-58, 30)),
        ("great_plains", "Great\nPlains", (-124, 17)), ("virgin_lands", "Kazakh\nsteppe", (82, 77))]
for out in outs("change"):
    fig = plt.figure(figsize=(7.6, 4.7), facecolor=BG)
    ax = fig.add_axes([0, .12, 1, .86]); world(ax, lambda i: LAND, lw=.2); draw_raster(ax, change_rgba(dfarm, 2000))
    for k, lab, (lx, ly) in LABS:
        b = CH["hotspots"][k]["box"]; cx, cy = ee((b[2] + b[3]) / 2, (b[0] + b[1]) / 2); tx, ty = ee(lx, ly)
        ax.annotate(lab, (cx, cy), (tx, ty), fontsize=7, color=FG, ha="center", va="center", zorder=5,
                    arrowprops=dict(arrowstyle="-", color=MUT, lw=.6, shrinkA=6, shrinkB=2))
    rampbar(fig, [.30, .085, .40, .022], CHG_NEG[::-1] + ["#F5F2EA"] + CHG_POS, "-60", "+60", "Change in farmland, percentage points of the land, 1900 to 2023")
    fig.text(.03, .005, "HYDE 3.3 baseline. Brown: more farmland. Teal: less.", fontsize=7.5, color=MUT)
    save(fig, out)

# ---------- 3. long series ----------
S0 = R["series"]; yrs = np.array(S0["years"]); cr = np.array(S0["crop"]); gz = np.array(S0["graz"])
for out in outs("series"):
    fig, ax = plt.subplots(figsize=(7.6, 4.2), facecolor=BG); ax.set_facecolor(BG)
    ax.stackplot(yrs, cr, gz, colors=[COL["crop"], COL["graz"]], alpha=.95)
    for y in YEARS:
        for v in (H[f"crop_{y}_km2"], H[f"farm_{y}_km2"]):
            ax.plot([y], [v / 1e6], "o", ms=6, mfc=BG, mec=FG, mew=1.4, zorder=5)
    ax.axvline(1900, color=MUT, lw=.8, ls=":")
    ax.text(1712, cr[0] / 2, "Cropland", fontsize=10, color=FG, va="center"); ax.text(1712, cr[0] + gz[0] / 2, "Grazing land", fontsize=10, color=FG, va="center")
    ax.text(1990, H["farm_2023_km2"] / 1e6 + 2.2, "dots: HYDE 3.3", fontsize=8.5, color=MUT, ha="center")
    ax.set_xlim(1700, 2025); ax.set_ylim(0, 55); ax.set_ylabel("million km²")
    ax.grid(axis="y", color=RULE, lw=.6); ax.set_axisbelow(True)
    fig.text(.01, .01, "HYDE 3.2 world totals (via Our World in Data); dots: HYDE 3.3 for 1900 and 2023.", fontsize=7.5, color=MUT)
    fig.tight_layout(rect=(0, .04, 1, 1)); save(fig, out)

# ---------- 4. regions ----------
RG = R["regions"]
for out in outs("regions"):
    fig, ax = plt.subplots(figsize=(7.6, 4.8), facecolor=BG); ax.set_facecolor(BG)
    ys = np.arange(len(RG))[::-1]; v = np.array([r["farm_chg_km2"] / 1e6 for r in RG])
    ax.barh(ys, v, color=[COL["gain"] if x >= 0 else COL["loss"] for x in v], height=.68)
    ax.set_yticks(ys); ax.set_yticklabels([r["name"] for r in RG], fontsize=9.5)
    for y_, x, r in zip(ys, v, RG):
        ax.text(max(x, 0) + .08, y_, f"{x:+.1f}  ({r['farm_1900_pct']:.0f}% → {r['farm_2023_pct']:.0f}%)", va="center", fontsize=8.5, color=FG)
    ax.axvline(0, color=MUT, lw=.8); ax.set_xlim(min(v) - .3, max(v) + 2.6); ax.set_xlabel("million km², 1900 to 2023")
    ax.spines[["left"]].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.text(.01, .01, "Change in cropland plus grazing land; brackets: share of ice-free land farmed. HYDE 3.3.", fontsize=7.5, color=MUT)
    fig.tight_layout(rect=(0, .04, 1, 1)); save(fig, out)

# ---------- 5. forest zone ----------
for out in outs("forest"):
    fig = plt.figure(figsize=(7.6, 4.9), facecolor=BG)
    ax = fig.add_axes([0, .13, 1, .85]); world(ax, lambda i: LAND, lw=.2)
    r, c, ok, h = ee_sample(2000)
    fzv = fw[r, c] & ok & (ml[r, c] > 0); cv = clr[2023][r, c]; dv = dclr[r, c]
    img = np.zeros((h, 2000, 4))
    g, t = hex2rgb("#3F7F5A"), hex2rgb("#D9A27A")
    img[fzv, :3] = g + (t - g) * np.clip(cv[fzv], 0, 1)[:, None]; img[fzv, 3] = .9
    m = fzv & (dv >= .1); img[m, :3] = hex2rgb("#8E2F14"); img[m, 3] = 1
    m = fzv & (dv <= -.1); img[m, :3] = hex2rgb("#1FA187"); img[m, 3] = 1
    draw_raster(ax, img)
    legend(fig, [("Forest zone, not farmed (2023)", "#3F7F5A"), ("Forest zone, farmed (2023)", "#D9A27A"),
                 ("Farmed share rose 10+ points since 1900", "#8E2F14"), ("Farmed share fell 10+ points: land back from farming", "#1FA187")], .13, ncol=2, fs=8.2)
    fig.text(.03, .005, "Forest zone: WWF potential forest biomes, via HYDE 3.3. Farmed: cropland, pasture or converted rangeland.", fontsize=7.2, color=MUT)
    save(fig, out)

# ---------- 6. anthromes ----------
keys = [g for g in AGROUP if g[0] != "ice"]
for out in outs("anthromes"):
    fig, ax = plt.subplots(figsize=(7.6, 2.9), facecolor=BG); ax.set_facecolor(BG)
    for j, y in enumerate((2023, 1900)):
        x = 0
        for k, l, c in keys:
            v = AN[f"{k}_{y}_pct"]; ax.barh(j, v, left=x, color=c, height=.62, edgecolor=BG, lw=.8)
            if v > 4.5: ax.text(x + v / 2, j, f"{v:.0f}%", ha="center", va="center", fontsize=8.5, color="#FFFFFF" if k in ("settle", "village", "semi", "wild") else FG)
            x += v
    ax.set_yticks([0, 1]); ax.set_yticklabels(["2023", "1900"], fontsize=11); ax.set_xlim(0, 100); ax.set_xlabel("% of ice-free land")
    ax.spines[["left"]].set_visible(False); ax.tick_params(axis="y", length=0)
    legend(fig, [(l, c) for k, l, c in keys], .995, ncol=6, fs=8, x=.02)
    fig.tight_layout(rect=(0, 0, 1, .86)); save(fig, out)

# ---------- 7. MODIS 2019 ----------
IG = {1: "#1B4D2E", 2: "#1F6B3A", 3: "#3E7A4E", 4: "#4F8F3E", 5: "#2F7A4A", 6: "#C3C26A", 7: "#C3C26A", 8: "#8FA65A", 9: "#C3C26A", 10: "#D7DE9A",
      11: "#5FA3A0", 12: "#E3A33B", 13: "#8E3A3A", 14: "#D6B868", 15: "#DDEBF2", 16: "#EDE2CB"}
mod = LW("modis5m")
for out in outs("modis"):
    fig = plt.figure(figsize=(7.6, 5.0), facecolor=BG)
    ax = fig.add_axes([0, .18, 1, .8]); world(ax, lambda i: LAND, lw=.2); draw_raster(ax, class_rgba(mod, 2000, IG))
    world(ax, lambda i: None, lw=.25, ec="#6B675E", z=3, fill=False)
    legend(fig, [("Forest", "#1F6B3A"), ("Woody savanna", "#8FA65A"), ("Savanna and shrubland", "#C3C26A"), ("Grassland", "#D7DE9A"),
                 ("Cropland", "#E3A33B"), ("Crop and natural mosaic", "#D6B868"), ("Barren (desert)", "#EDE2CB"), ("Snow and ice", "#DDEBF2"), ("Urban", "#8E3A3A"), ("Wetland", "#5FA3A0")], .18, ncol=5, fs=7.8)
    fig.text(.03, .005, "MODIS MCD12C1 v006, 2019, IGBP classes at 0.05 degrees (NASA). Shrublands and savannas share a colour here.", fontsize=7.2, color=MUT)
    save(fig, out)
print("figures done")
