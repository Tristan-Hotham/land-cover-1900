"""Read the HYDE 3.3 ESRI ASCII grids (5 arc-min, 4320 x 2160) into compact .npy arrays in memory (WORK, on disk outside the repo)."""
import numpy as np, rasterio
from common import *

def load(path, name):
    out = f"{WORK}/{name}.npy"
    if os.path.exists(out):
        return
    try:
        with rasterio.open(path) as r:
            a = r.read(1, masked=True).astype(np.float32).filled(np.nan)
    except rasterio.errors.RasterioIOError:      # forest_wwf_cr.asc has an indented header GDAL rejects: parse by hand
        with open(path) as f:
            head = [next(f).split() for _ in range(6)]
            nd = float(head[5][1])
            a = np.fromstring(f.read(), dtype=np.float32, sep=" ").reshape(2160, 4320)
        a[a == nd] = np.nan
    assert a.shape == (2160, 4320), (path, a.shape)
    np.save(out, a)
    print(name, np.nanmin(a), np.nanmax(a))

for y in YEARS:
    for v in ["cropland", "grazing", "pasture", "rangeland", "conv_rangeland"]:
        load(f"{RAW_GRID}/{y}AD_lu/{v}{y}AD.asc", f"{v}{y}")
    load(f"{RAW_GRID}/{y}AD_anthromes/anthromes{y}AD.asc", f"anthromes{y}")
for v in ["garea_cr", "maxln_cr", "iso_cr", "forest_wwf_cr"]:
    load(f"{GEN}/{v}.asc", v)

# MODIS MCD12C1 2019 (0.05 deg IGBP majority class): class fractions on the 0.25 deg grid (5 x 5 MODIS cells), for the
# cross-check against HYDE (5 arc-min x 3 = 0.25 deg), and a nearest-centre 5 arc-min class grid for the maps
out = f"{WORK}/modis_q.npz"
if not os.path.exists(out):
    with rasterio.open(MODIS) as r:
        m = r.read(1)
    q = {}
    for c in range(0, 17):
        q[f"c{c}"] = (m == c).astype(np.float32).reshape(720, 5, 1440, 5).mean(axis=(1, 3))
    np.savez_compressed(out, **q)
    lat = 90 - (np.arange(2160) + .5) / 12; lon = -180 + (np.arange(4320) + .5) / 12
    ri = np.clip(((90 - lat) / 0.05).astype(int), 0, 3599); ci = np.clip(((lon + 180) / 0.05).astype(int), 0, 7199)
    np.save(f"{WORK}/modis5m.npy", m[np.ix_(ri, ci)].astype(np.uint8))
    print("modis done")
