"""Page grids: HYDE 3.3 summed from 5 to 10 arc-minutes (2160 x 864 cells, 84N to 60S), written as RGB PNGs that the
page decodes in the browser. Shares are of the land in each cell, coded 0 to 250 (0.4% steps).
  data/page/g1.png : R cropland 1900, G cropland 2023, B land share of the cell (land / cell area)
  data/page/g2.png : R grazing land 1900, G grazing land 2023, B share of the land in the potential forest zone
  data/page/g3.png : R pasture 1900, G pasture 2023, B MODIS 2019 IGBP class (nearest 0.05 degree pixel, 0 water, 255 none)
  data/page/g4.png : R cleared forest zone 1900, G cleared 2023 (both as share of the cell's land), B anthrome 1900 (index)
  data/page/g5.png : R anthrome 2023 (index), G and B the HYDE country code (G * 256 + B)
Anthrome index: 1 + position in common.ANTH (0 = none); the anthrome of a 10' cell is the one covering most of its land.
Also data/site.json (country names by HYDE code, label points, anthrome and region lists) and
data/hyde33_10arcmin_1900_2023.tif (GeoTIFF of the same layers in km2 for reuse)."""
import numpy as np, pandas as pd
from PIL import Image
import rasterio
from rasterio.transform import from_origin
from common import *

L = lambda n: np.nan_to_num(np.load(f"{WORK}/{n}.npy"))
N0, S0 = 84, -60
r0, r1 = (90 - N0) * 12, (90 - S0) * 12
cut = lambda a: a[r0:r1]
agg = lambda a: cut(a).reshape((r1 - r0) // 2, 2, 4320 // 2, 2).sum(axis=(1, 3))
ml = L("maxln_cr"); ga = L("garea_cr"); fw = (L("forest_wwf_cr") > .5).astype(np.float32)
ml10, ga10 = agg(ml), agg(ga)
den = np.maximum(ml10, 1e-6)
enc = lambda km2: np.clip(np.round(250 * km2 / den), 0, 250).astype(np.uint8) * (ml10 > 0)
lay = {}
for y in YEARS:
    c, p, r, cv = [L(f"{v}{y}") for v in ("cropland", "pasture", "rangeland", "conv_rangeland")]
    lay[f"crop{y}"] = agg(c); lay[f"graz{y}"] = agg(p + r + cv); lay[f"past{y}"] = agg(p); lay[f"clr{y}"] = agg((c + p + cv) * fw)
landsh = np.clip(np.round(250 * ml10 / np.maximum(ga10, 1e-6)), 0, 250).astype(np.uint8)
fzs = enc(agg(ml * fw))
mod = np.load(f"{WORK}/modis5m.npy")[r0:r1][::2, ::2].copy()
mod[ml10 <= 0] = 0
code = {c: i + 1 for i, (c, n, g) in enumerate(ANTH)}
ANT = {}
for y in YEARS:
    a = L(f"anthromes{y}").astype(int)
    best = np.zeros(ml10.shape, np.float32); idx = np.zeros(ml10.shape, np.uint8)
    for c, i in code.items():
        s = agg(ml * (a == c))
        m = s > best; best[m] = s[m]; idx[m] = i
    ANT[y] = idx
iso = cut(L("iso_cr").astype(int))
# country of a 10' cell: the code of its top-left 5' land cell, else any land cell
iso10 = iso[::2, ::2].copy()
for dy in (0, 1):
    for dx in (0, 1):
        o = iso[dy::2, dx::2]
        iso10 = np.where(iso10 > 0, iso10, o)
iso10[ml10 <= 0] = 0
iso10 = np.clip(iso10, 0, 65535)
P = lambda *ch: Image.fromarray(np.dstack(ch).astype(np.uint8), "RGB")
P(enc(lay["crop1900"]), enc(lay["crop2023"]), landsh).save(f"{PAGE_D}/g1.png", optimize=True)
P(enc(lay["graz1900"]), enc(lay["graz2023"]), fzs).save(f"{PAGE_D}/g2.png", optimize=True)
P(enc(lay["past1900"]), enc(lay["past2023"]), mod).save(f"{PAGE_D}/g3.png", optimize=True)
P(enc(lay["clr1900"]), enc(lay["clr2023"]), ANT[1900]).save(f"{PAGE_D}/g4.png", optimize=True)
P(ANT[2023], (iso10 >> 8).astype(np.uint8), (iso10 & 255).astype(np.uint8)).save(f"{PAGE_D}/g5.png", optimize=True)
tot = 0
for fn in sorted(os.listdir(PAGE_D)):
    kb = os.path.getsize(f"{PAGE_D}/{fn}") // 1024; tot += kb; print(fn, kb, "KB")
print("page grids", tot, "KB")

# reusable GeoTIFF (km2 per 10' cell)
bands = [("land_km2", ml10)] + [(f"{k}_km2", lay[k]) for k in ("crop1900", "crop2023", "graz1900", "graz2023", "past1900", "past2023", "clr1900", "clr2023")]
bands += [("forest_zone_km2", agg(ml * fw))]
with rasterio.open(f"{DATA}/hyde33_10arcmin_1900_2023.tif", "w", driver="GTiff", height=ml10.shape[0], width=ml10.shape[1], count=len(bands) + 2,
                   dtype="float32", crs="EPSG:4326", transform=from_origin(-180, N0, 1 / 6, 1 / 6), compress="deflate", predictor=3) as d:
    for i, (n, a) in enumerate(bands, 1):
        d.write(a.astype(np.float32), i); d.update_tags(i, name=n)
    d.write(ANT[1900].astype(np.float32), len(bands) + 1); d.update_tags(len(bands) + 1, name="anthrome_1900_index (1 + position in README list)")
    d.write(ANT[2023].astype(np.float32), len(bands) + 2); d.update_tags(len(bands) + 2, name="anthrome_2023_index")
    d.update_tags(source="Derived from HYDE 3.3 baseline (Klein Goldewijk et al.), CC BY 4.0, DOI " + HYDE_DOI)
print("tif", os.path.getsize(f"{DATA}/hyde33_10arcmin_1900_2023.tif") // 1024, "KB")

# site.json: names by HYDE code, countries' summary rows for the side panel, label points
cdf = pd.read_csv(f"{DATA}/country_landuse_1900_2023.csv", keep_default_na=False)
cg = jload(f"{DATA}/countries_geo.json")
site = {"hc": {}, "c": {}, "cpos": {k: [v["lon"], v["lat"], v["pop"]] for k, v in cg.items()}, "cname": {k: v["name"] for k, v in cg.items()},
        "anth": [[n, g] for c, n, g in ANTH], "agroup": AGROUP, "grid": {"w": 2160, "h": 864, "top": N0, "cell": 1 / 6}}
for _, r in cdf.iterrows():
    site["hc"][int(r.hyde_code)] = [r.iso3, r["name"]]
    if r.iso3 and r.land_km2 >= 50:
        prev = site["c"].get(r.iso3)
        row = [r.land_km2, r.ice_km2, r.forest_zone_km2, r.crop_1900_km2, r.crop_2023_km2, r.graz_1900_km2, r.graz_2023_km2,
               r.cleared_1900_km2, r.cleared_2023_km2, r.wild_1900_km2, r.wild_2023_km2, r.past_1900_km2, r.past_2023_km2]
        site["c"][r.iso3] = [round(a + (prev[i] if prev else 0)) for i, a in enumerate(row)]
jsave(site, f"{DATA}/site.json")
print("site.json", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
