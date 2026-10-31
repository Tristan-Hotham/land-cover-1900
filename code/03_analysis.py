"""All the numbers. HYDE 3.3 (baseline) land use for 1900 and 2023 on its 5 arc-minute grid, the HYDE anthromes for both
years, the WWF potential forest zone from the HYDE general files, and MODIS MCD12C1 2019 land cover as a cross-check.
Writes data/results.json (sections hyde, forest, anthromes, change, regions, countries, modis, series, uk) and the
reusable tables data/country_landuse_1900_2023.csv, data/region_landuse_1900_2023.csv and data/hyde32_world_1700_2016.csv.

Definitions (also in the paper):
  land        HYDE maximum land area per cell (maxln_cr), km2; Antarctica is not in the HYDE grid
  ice         land in cells of the anthrome 'Ice, uninhabited' (63) in the year in question
  farmland    cropland + grazing land; grazing land = pasture + rangeland + converted rangeland (HYDE 3.3)
  forest zone cells where the WWF biome map used by HYDE has forest as the potential (natural) vegetation (forest_wwf_cr = 1)
  cleared     cropland + pasture + converted rangeland inside the forest zone: the forest-zone land in farming use
  uncleared   forest-zone land minus cleared land: forest, regrowth, woodland, and anything else not farmed"""
import numpy as np, pandas as pd
from common import *

L = lambda n: np.nan_to_num(np.load(f"{WORK}/{n}.npy"))
ml = L("maxln_cr"); fw = (L("forest_wwf_cr") > 0.5).astype(np.float32); iso = L("iso_cr").astype(int)
ga = L("garea_cr")
lat = 90 - (np.arange(2160) + .5) / 12; lon = -180 + (np.arange(4320) + .5) / 12
LAT = np.broadcast_to(lat[:, None], ml.shape); LON = np.broadcast_to(lon[None, :], ml.shape)
A = {y: L(f"anthromes{y}").astype(int) for y in YEARS}
G = {}
for y in YEARS:
    c, p, r, cv = [L(f"{v}{y}") for v in ("cropland", "pasture", "rangeland", "conv_rangeland")]
    G[y] = {"crop": c, "past": p, "range": r, "conv": cv, "graz": p + r + cv, "farm": c + p + r + cv, "clr": (c + p + cv) * fw}
    assert np.allclose(G[y]["graz"], L(f"grazing{y}"), atol=0.05), "grazing = pasture + rangeland + converted rangeland"
    assert float((r * fw).sum()) == 0 and float((cv * (1 - fw)).sum()) == 0, "converted rangeland only in the forest zone"
    assert (G[y]["farm"] <= ml * 1.001 + 1e-3).all()
M = 1e6
S = lambda a: float(a.sum())

# ---------------- global totals ----------------
land = S(ml)
H = {"land_km2": land}
for y in YEARS:
    ice = S(ml * (A[y] == 63)); H[f"ice_{y}_km2"] = ice
icefree = land - H["ice_2023_km2"]
H["icefree_km2"] = icefree
for y in YEARS:
    for k in ("crop", "past", "range", "conv", "graz", "farm"):
        H[f"{k}_{y}_km2"] = S(G[y][k])
        H[f"{k}_{y}_pct"] = 100 * S(G[y][k]) / icefree
for k in ("crop", "graz", "farm", "past"):
    H[f"{k}_x"] = H[f"{k}_2023_km2"] / H[f"{k}_1900_km2"]
    H[f"{k}_gain_km2"] = H[f"{k}_2023_km2"] - H[f"{k}_1900_km2"]
H["farm_gain_vs_us"] = H["farm_gain_km2"] / 9.15e6     # USA land area (World Bank) for comparison in the text
fc = G[2023]["farm"] - G[1900]["farm"]
H["farm_gross_gain_km2"] = S(np.maximum(fc, 0)); H["farm_gross_loss_km2"] = -S(np.minimum(fc, 0))
assert 18 < H["farm_1900_pct"] < 21 and 36 < H["farm_2023_pct"] < 39, (H["farm_1900_pct"], H["farm_2023_pct"])
assert 1.75 < H["crop_x"] < 1.85 and 1.95 < H["graz_x"] < 2.1
results = {"hyde": H}

# ---------------- forest zone ----------------
fz = S(ml * fw)
F = {"zone_km2": fz, "zone_pct_icefree": 100 * fz / icefree}
for y in YEARS:
    F[f"cleared_{y}_km2"] = S(G[y]["clr"]); F[f"cleared_{y}_pct"] = 100 * S(G[y]["clr"]) / fz
    F[f"uncleared_{y}_pct"] = 100 - F[f"cleared_{y}_pct"]
    F[f"crop_{y}_km2"] = S(G[y]["crop"] * fw)
ch = G[2023]["clr"] - G[1900]["clr"]
F["net_km2"] = F["cleared_2023_km2"] - F["cleared_1900_km2"]
F["gross_gain_km2"] = S(np.maximum(ch, 0)); F["gross_loss_km2"] = -S(np.minimum(ch, 0))
F["share_farm_gain_in_zone_pct"] = 100 * F["net_km2"] / H["farm_gain_km2"]
F["outside_crop_2023_pct"] = 100 * S(G[2023]["crop"] * (1 - fw)) / H["crop_2023_km2"]
assert 0 < F["gross_loss_km2"] < F["gross_gain_km2"]
results["forest"] = F

# ---------------- anthromes ----------------
AN = {}
code_group = {c: g for c, n, g in ANTH}
for y in YEARS:
    grp = {}
    for c, n, g in ANTH:
        a = S(ml * (A[y] == c)); AN[f"c{c}_{y}_km2"] = a; grp[g] = grp.get(g, 0) + a
    for g, a in grp.items():
        AN[f"{g}_{y}_km2"] = a; AN[f"{g}_{y}_pct"] = 100 * a / icefree if g != "ice" else 100 * a / land
    AN[f"wildwood_{y}_km2"] = AN[f"c61_{y}_km2"]
    AN[f"used_{y}_pct"] = 100 * sum(grp[g] for g in ("settle", "village", "crop", "range")) / icefree
for g in ("wild", "semi", "settle", "village", "crop", "range"):
    AN[f"{g}_chg_km2"] = AN[f"{g}_2023_km2"] - AN[f"{g}_1900_km2"]
AN["wildwood_chg_pct"] = 100 * (AN["wildwood_2023_km2"] / AN["wildwood_1900_km2"] - 1)
AN["urban_x"] = AN["c11_2023_km2"] / AN["c11_1900_km2"]
AN["settle_x"] = AN["settle_2023_km2"] / AN["settle_1900_km2"]
# where was wild in 1900 and what became of it (share of 1900 wildland, excluding ice, by 2023 group)
w0 = np.isin(A[1900], [61, 62])
tw = S(ml * w0)
AN["wild1900_to"] = {g: 100 * S(ml * w0 * np.isin(A[2023], [c for c, n, gg in ANTH if gg == g])) / tw for g, _, _ in AGROUP}
assert abs(sum(AN["wild1900_to"].values()) - 100) < 0.01
# wild woodlands in the forest zone, by latitude band in 2023 (boreal north of 50N vs tropics)
ww = ml * (A[2023] == 61)
AN["wildwood_2023_north50_pct"] = 100 * S(ww * (LAT >= 50)) / S(ww)
AN["wildwood_2023_tropics_pct"] = 100 * S(ww * (np.abs(LAT) < 23.44)) / S(ww)
results["anthromes"] = AN

# ---------------- countries and regions ----------------
cg = jload(f"{DATA}/countries_geo.json")
n3 = {}
for k, v in cg.items():
    try:
        n3[int(v["n3"])] = k
    except (TypeError, ValueError):
        pass
n3.update({175: "FRA", 254: "FRA", 312: "FRA", 474: "FRA", 638: "FRA", 736: "SDN", 830: "GBR", 158: "TWN", 891: "SRB", 530: "CUW", 744: "NOR", 248: "FIN", 732: "ESH"})
xc = pd.read_excel(COUNTRY_CODES).iloc[:, :2]; xc.columns = ["n", "name"]
hname = {int(a): str(b).strip() for a, b in zip(xc.n, xc.name) if pd.notna(a)}
REGION = {"Northern Europe": "Europe", "Western Europe": "Europe", "Southern Europe": "Europe", "Eastern Europe": "Europe",
          "Northern America": "North America", "Central America": "Central America and Caribbean",
          "Caribbean": "Central America and Caribbean", "South America": "South America", "Northern Africa": "North Africa and West Asia",
          "Western Asia": "North Africa and West Asia", "Eastern Africa": "Sub-Saharan Africa", "Western Africa": "Sub-Saharan Africa",
          "Middle Africa": "Sub-Saharan Africa", "Southern Africa": "Sub-Saharan Africa", "Central Asia": "Central Asia",
          "Southern Asia": "South Asia", "Eastern Asia": "East Asia", "South-Eastern Asia": "Southeast Asia",
          "Australia and New Zealand": "Oceania", "Melanesia": "Oceania", "Micronesia": "Oceania", "Polynesia": "Oceania",
          "Seven seas (open ocean)": "Oceania"}


def region_of(i3):
    if i3 == "RUS": return "Russia"
    if i3 == "SDN": return "North Africa and West Asia"
    sub = cg.get(i3, {}).get("subregion")
    return REGION.get(sub, "Other")


codes = np.unique(iso[ml > 0])
iso3 = {int(c): n3.get(int(c)) for c in codes}
miss = {c: hname.get(c) for c, v in iso3.items() if v is None}
rows = []
flat = {"ml": lambda: ml, "fz": lambda: ml * fw, "ice": lambda: ml * (A[2023] == 63),
        "c0": lambda: G[1900]["crop"], "c1": lambda: G[2023]["crop"], "g0": lambda: G[1900]["graz"], "g1": lambda: G[2023]["graz"],
        "p0": lambda: G[1900]["past"], "p1": lambda: G[2023]["past"], "k0": lambda: G[1900]["clr"], "k1": lambda: G[2023]["clr"],
        "w0": lambda: ml * np.isin(A[1900], [61, 62]), "w1": lambda: ml * np.isin(A[2023], [61, 62]),
        "s0": lambda: ml * np.isin(A[1900], [11, 12]), "s1": lambda: ml * np.isin(A[2023], [11, 12]),
        "nf": lambda: np.minimum(fc, 0), "nk": lambda: np.minimum(ch, 0)}
idx = iso.ravel()
sums = {k: np.bincount(idx, weights=v().ravel(), minlength=1000) for k, v in flat.items()}
for c in codes:
    c = int(c); i3 = iso3[c]
    r = {"hyde_code": c, "iso3": i3 or "", "name": cg[i3]["name"] if i3 in cg else hname.get(c, str(c)),
         "region": region_of(i3) if i3 else "Other"}
    for k, col in (("ml", "land_km2"), ("fz", "forest_zone_km2"), ("ice", "ice_km2"), ("c0", "crop_1900_km2"), ("c1", "crop_2023_km2"),
                   ("g0", "graz_1900_km2"), ("g1", "graz_2023_km2"), ("p0", "past_1900_km2"), ("p1", "past_2023_km2"),
                   ("k0", "cleared_1900_km2"), ("k1", "cleared_2023_km2"), ("w0", "wild_1900_km2"), ("w1", "wild_2023_km2"),
                   ("s0", "settle_1900_km2"), ("s1", "settle_2023_km2"), ("nf", "farm_gross_loss_km2"), ("nk", "cleared_gross_loss_km2")):
        r[col] = round(float(sums[k][c]), 1)
    rows.append(r)
cdf = pd.DataFrame(rows)
cdf["farm_1900_km2"] = cdf.crop_1900_km2 + cdf.graz_1900_km2
cdf["farm_2023_km2"] = cdf.crop_2023_km2 + cdf.graz_2023_km2
cdf["farm_chg_km2"] = cdf.farm_2023_km2 - cdf.farm_1900_km2
cdf["cleared_chg_km2"] = cdf.cleared_2023_km2 - cdf.cleared_1900_km2
cdf["crop_chg_km2"] = cdf.crop_2023_km2 - cdf.crop_1900_km2
fl = (cdf.land_km2 - cdf.ice_km2).clip(lower=1)
for y in YEARS:
    cdf[f"farm_{y}_pct"] = (100 * cdf[f"farm_{y}_km2"] / fl).round(2)
    cdf[f"cleared_{y}_pct_of_zone"] = np.where(cdf.forest_zone_km2 > 0, (100 * cdf[f"cleared_{y}_km2"] / cdf.forest_zone_km2.clip(lower=1)).round(2), np.nan)
cdf = cdf.sort_values("land_km2", ascending=False)
cdf.round(2).to_csv(f"{DATA}/country_landuse_1900_2023.csv", index=False)
big = cdf[cdf.land_km2 >= 1000]

top = lambda col, n, asc=False: [{"iso": r.iso3, "name": r["name"], "v": float(r[col])} for _, r in big.sort_values(col, ascending=asc).head(n).iterrows()]
CH = {"top_farm_gain": top("farm_chg_km2", 10), "top_farm_loss": top("farm_chg_km2", 8, True), "top_clear_gain": top("cleared_chg_km2", 10),
      "top_clear_loss": top("cleared_chg_km2", 8, True), "top_crop_gain": top("crop_chg_km2", 8), "top_crop_loss": top("crop_chg_km2", 8, True),
      "n_farm_down": int((big.farm_chg_km2 < 0).sum()), "n_countries": int(len(big))}
cpos = lambda i3: next(x for x in CH["top_farm_gain"] if x["iso"] == i3)
BR = cdf[cdf.iso3 == "BRA"].iloc[0]; US = cdf[cdf.iso3 == "USA"].iloc[0]
CH["BRA"] = {k: float(BR[k]) for k in ("farm_chg_km2", "cleared_chg_km2", "crop_chg_km2", "cleared_1900_pct_of_zone", "cleared_2023_pct_of_zone", "farm_1900_pct", "farm_2023_pct")}
CH["USA"] = {k: float(US[k]) for k in ("farm_chg_km2", "cleared_chg_km2", "farm_gross_loss_km2", "cleared_gross_loss_km2", "farm_1900_pct", "farm_2023_pct")}
# eastern United States (east of 90W) and Europe: land that went out of farming
usm = (iso == 840)
eus = usm & (LON > -90)
CH["east_us"] = {"cleared_1900_km2": S(G[1900]["clr"] * eus), "cleared_2023_km2": S(G[2023]["clr"] * eus),
                 "zone_km2": S(ml * fw * eus)}
CH["east_us"]["net_km2"] = CH["east_us"]["cleared_2023_km2"] - CH["east_us"]["cleared_1900_km2"]
CH["east_us"]["c1900_pct"] = 100 * CH["east_us"]["cleared_1900_km2"] / CH["east_us"]["zone_km2"]
CH["east_us"]["c2023_pct"] = 100 * CH["east_us"]["cleared_2023_km2"] / CH["east_us"]["zone_km2"]
CH["east_us"]["share_of_us_gross_loss_pct"] = 100 * S(np.minimum(ch, 0) * eus) / S(np.minimum(ch, 0) * usm)
eu = cdf[cdf.region == "Europe"]
CH["europe"] = {"farm_chg_km2": float(eu.farm_chg_km2.sum()), "farm_gross_loss_km2": float(eu.farm_gross_loss_km2.sum()),
                "cleared_1900_pct": float(100 * eu.cleared_1900_km2.sum() / eu.forest_zone_km2.sum()),
                "cleared_2023_pct": float(100 * eu.cleared_2023_km2.sum() / eu.forest_zone_km2.sum()),
                "n_down": int((eu[eu.land_km2 >= 1000].farm_chg_km2 < 0).sum()), "n": int((eu.land_km2 >= 1000).sum())}
CH["gross_loss_share_us_europe_russia_pct"] = 100 * float(cdf[cdf.region.isin(["Europe", "Russia"]) | (cdf.iso3 == "USA")].cleared_gross_loss_km2.sum()) / float(cdf.cleared_gross_loss_km2.sum())
# named hotspots (boxes, land cells only): farmland, cropland and forest-zone clearing change
BOX = {"cerrado": ("Brazilian Cerrado", -24, -2, -60, -41, 76), "amazon_arc": ("Southern Amazon arc", -15, -2, -70, -44, 76),
       "pampas": ("Argentine Pampas", -40, -27, -66, -56, 32), "great_plains": ("US Great Plains", 30, 49, -105, -95, 840),
       "midwest": ("US Midwest and Corn Belt", 36, 49, -95, -80, 840), "virgin_lands": ("Kazakh steppe", 46, 55, 60, 80, 398),
       "sahel": ("Sahel", 10, 17, -17, 38, None), "se_asia": ("Southeast Asia", -11, 24, 92, 141, None),
       "wheatbelt": ("Australian wheat belt", -36, -26, 113, 125, 36), "east_us": ("Eastern United States", 24, 50, -90, -66, 840),
       "europe_w": ("Western and central Europe", 36, 60, -10, 25, None)}
HS = {}
for k, (nm, s_, n_, w_, e_, cc) in BOX.items():
    m = (LAT >= s_) & (LAT <= n_) & (LON >= w_) & (LON <= e_)
    if cc: m &= (iso == cc)
    zz = S(ml * fw * m)
    HS[k] = {"name": nm, "box": [s_, n_, w_, e_], "land_km2": S(ml * m), "farm_1900_km2": S(G[1900]["farm"] * m), "farm_2023_km2": S(G[2023]["farm"] * m),
             "crop_1900_km2": S(G[1900]["crop"] * m), "crop_2023_km2": S(G[2023]["crop"] * m),
             "cleared_1900_km2": S(G[1900]["clr"] * m), "cleared_2023_km2": S(G[2023]["clr"] * m), "zone_km2": zz}
    h = HS[k]
    h["farm_chg_km2"] = h["farm_2023_km2"] - h["farm_1900_km2"]; h["crop_chg_km2"] = h["crop_2023_km2"] - h["crop_1900_km2"]
    h["farm_1900_pct"] = 100 * h["farm_1900_km2"] / h["land_km2"]; h["farm_2023_pct"] = 100 * h["farm_2023_km2"] / h["land_km2"]
    h["crop_1900_pct"] = 100 * h["crop_1900_km2"] / h["land_km2"]; h["crop_2023_pct"] = 100 * h["crop_2023_km2"] / h["land_km2"]
CH["hotspots"] = HS
results["change"] = CH
# regions
reg = cdf.groupby("region")[["land_km2", "ice_km2", "forest_zone_km2", "crop_1900_km2", "crop_2023_km2", "graz_1900_km2", "graz_2023_km2",
                             "cleared_1900_km2", "cleared_2023_km2", "wild_1900_km2", "wild_2023_km2", "farm_gross_loss_km2"]].sum()
reg["farm_1900_km2"] = reg.crop_1900_km2 + reg.graz_1900_km2; reg["farm_2023_km2"] = reg.crop_2023_km2 + reg.graz_2023_km2
reg["farm_chg_km2"] = reg.farm_2023_km2 - reg.farm_1900_km2; reg["cleared_chg_km2"] = reg.cleared_2023_km2 - reg.cleared_1900_km2
reg["farm_1900_pct"] = 100 * reg.farm_1900_km2 / (reg.land_km2 - reg.ice_km2); reg["farm_2023_pct"] = 100 * reg.farm_2023_km2 / (reg.land_km2 - reg.ice_km2)
reg = reg.drop(index=[x for x in reg.index if x == "Other"], errors="ignore").sort_values("farm_chg_km2", ascending=False)
reg.round(1).to_csv(f"{DATA}/region_landuse_1900_2023.csv")
results["regions"] = [{"name": n, **{k: float(v) for k, v in r.items()}} for n, r in reg.iterrows()]
assert results["regions"][-1]["name"] == "Europe" and results["regions"][-1]["farm_chg_km2"] < 0
results["countries"] = {"missing_codes": {str(k): v for k, v in miss.items()}, "n": int(len(cdf))}

# ---------------- MODIS 2019 cross-check ----------------
q = np.load(f"{WORK}/modis_q.npz")
agg = lambda a: a.reshape(720, 3, 1440, 3).sum(axis=(1, 3))
ml_q, fz_q = agg(ml), agg(ml * fw)
fzf = np.where(ml_q > 0, fz_q / np.maximum(ml_q, 1e-9), 0)
mf = sum(q[f"c{c}"] for c in (1, 2, 3, 4, 5)); mws = q["c8"]; mcr = q["c12"] + 0.5 * q["c14"]; mur = q["c13"]; mice = q["c15"]; mbar = q["c16"]
mland = 1 - q["c0"]
MO = {}
landq = np.where(mland > 0, ml_q / np.maximum(mland, 1e-9), 0)    # HYDE land in each 0.25 deg cell spread over MODIS land
area_of = lambda frac: float((frac * landq).sum())
MO["forest_km2"] = area_of(mf); MO["woody_savanna_km2"] = area_of(mws); MO["crop_km2"] = area_of(mcr); MO["urban_km2"] = area_of(mur)
MO["ice_km2"] = area_of(mice); MO["barren_km2"] = area_of(mbar)
MO["forest_in_zone_pct"] = 100 * float((mf * landq * fzf).sum()) / float(fz_q.sum())
MO["treecover_in_zone_pct"] = 100 * float(((mf + mws) * landq * fzf).sum()) / float(fz_q.sum())
MO["crop_vs_hyde_pct"] = 100 * MO["crop_km2"] / H["crop_2023_km2"]
hcl = agg(G[2023]["clr"]); hfz = fz_q
ok = hfz > 50
x = 100 * hcl[ok] / hfz[ok]; y = 100 * (1 - (mf + mws)[ok] * landq[ok] * fzf[ok] / np.maximum(hfz[ok], 1e-9))
MO["r_cleared_vs_nontree"] = float(np.corrcoef(x, np.clip(y, 0, 100))[0, 1])
MO["n_cells"] = int(ok.sum())
results["modis"] = MO

# ---------------- long series (HYDE 3.2 via OWID, world) ----------------
d = pd.read_csv(OWID_HYDE32)
w = d[d.Entity == "World"].set_index("Year").sort_index()
w = w[w.index >= 1700]
ser = pd.DataFrame({"cropland_km2": w["Cropland (HYDE (2017))"] / 100, "grazing_km2": w["Grazing (HYDE (2017))"] / 100,
                    "builtup_km2": w["Built-up Area (HYDE (2017))"] / 100})
ser.index.name = "year"
ser.round(0).to_csv(f"{DATA}/hyde32_world_1700_2016.csv")
results["series"] = {"years": [int(v) for v in ser.index], "crop": [round(v / M, 3) for v in ser.cropland_km2], "graz": [round(v / M, 3) for v in ser.grazing_km2],
                     "built": [round(v / M, 4) for v in ser.builtup_km2], "src": "HYDE 3.2 (Klein Goldewijk et al. 2017), via Our World in Data",
                     "crop_1900_v32_km2": float(ser.cropland_km2[1900]), "graz_1900_v32_km2": float(ser.grazing_km2[1900]),
                     "farm_1700_km2": float(ser.cropland_km2[1700] + ser.grazing_km2[1700]), "farm_1900_v32_km2": float(ser.cropland_km2[1900] + ser.grazing_km2[1900]),
                     "farm_1950_km2": float(ser.cropland_km2[1950] + ser.grazing_km2[1950])}
sr = results["series"]
sr["farm_1700_1900_gain_km2"] = sr["farm_1900_v32_km2"] - sr["farm_1700_km2"]
sr["farm_1900_1950_gain_km2"] = sr["farm_1950_km2"] - sr["farm_1900_v32_km2"]
f90 = float(ser.cropland_km2[1990] + ser.grazing_km2[1990]); f16 = float(ser.cropland_km2[2016] + ser.grazing_km2[2016])
sr["farm_1950_1990_gain_km2"] = f90 - sr["farm_1950_km2"]; sr["farm_1990_2016_gain_km2"] = f16 - f90
assert abs(sr["crop_1900_v32_km2"] / H["crop_1900_km2"] - 1) < 0.1      # HYDE 3.2 and 3.3 agree within 10% for 1900 cropland

# ---------------- UK ----------------
uk = cdf[cdf.iso3 == "GBR"].iloc[0]
results["uk"] = {k: float(uk[k]) for k in ("land_km2", "crop_1900_km2", "crop_2023_km2", "graz_1900_km2", "graz_2023_km2", "farm_1900_pct", "farm_2023_pct")}

# round floats for readability
def rnd(o):
    if isinstance(o, float): return round(o, 3) if abs(o) < 1000 else round(o, 1)
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list): return [rnd(v) for v in o]
    return o


R = jload(f"{DATA}/results.json") if os.path.exists(f"{DATA}/results.json") else {}
R.update(rnd(results))
R["meta"] = {"hyde": "HYDE 3.3 baseline (hyde33_c7_base_mrt2023)", "hyde_doi": HYDE_DOI, "years": list(YEARS), "grid": "5 arc-minutes",
             "modis": "MODIS MCD12C1 v006, 2019"}
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("hyde", "forest", "modis")}, indent=1))
print(json.dumps(R["anthromes"]["wild1900_to"], indent=1), R["change"]["east_us"], R["change"]["europe"])
for k, h in R["change"]["hotspots"].items():
    print(f"{h['name']:30s} farm {h['farm_1900_pct']:.0f}->{h['farm_2023_pct']:.0f}% crop {h['crop_1900_pct']:.0f}->{h['crop_2023_pct']:.0f}% chg {h['farm_chg_km2']/1e3:.0f}k")
print([(r["name"], round(r["farm_chg_km2"] / 1e3), round(r["cleared_chg_km2"] / 1e3), round(r["farm_1900_pct"]), round(r["farm_2023_pct"])) for r in R["regions"]])
print("missing", R["countries"]["missing_codes"])
