"""README.md and LICENSE, with every number from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json"); H, F, AN, CH, MO = R["hyde"], R["forest"], R["anthromes"], R["change"], R["modis"]
HS = CH["hotspots"]
sz = lambda p: f"{os.path.getsize(os.path.join(ROOT, p)) / 1e6:.1f} MB"
doi = f"https://doi.org/{DOI}" if not DOI.startswith("{{") else "https://doi.org/10.5281/zenodo.23847971"
m = lambda v: f"{v / 1e6:.1f}"
md = f"""# Desert, forest, ice: the world in 1900 and now

The world's land in 1900 and 2023 on one swipe map: cropland, grazing land, farming in the natural forest zone, anthromes (wild, seminatural and used land) and present-day satellite land cover. Built from the HYDE 3.3 historical land use reconstruction (5 arc-minute grids) and MODIS MCD12C1 land cover for 2019.

Interactive page: {PAGE}
Paper: {doi}
Blog post: {BLOG}

## Headline results

- Farmland (cropland plus grazing land) covered {H['farm_1900_pct']:.1f}% of the world's ice-free land in 1900 and {H['farm_2023_pct']:.1f}% in 2023 (HYDE 3.3 baseline; Antarctica excluded). Cropland grew from {m(H['crop_1900_km2'])} to {m(H['crop_2023_km2'])} million km², grazing land from {m(H['graz_1900_km2'])} to {m(H['graz_2023_km2'])} million km². The net gain, {m(H['farm_gain_km2'])} million km², is {H['farm_gain_vs_us']:.1f} times the area of the United States.
- Where: the largest gains were in sub-Saharan Africa (+{m(R['regions'][0]['farm_chg_km2'])} million km²) and South America (+{m(R['regions'][1]['farm_chg_km2'])}); by country China, Brazil and Australia (each more than 2 million km²). Europe is the only region with less farmland than in 1900 ({m(CH['europe']['farm_chg_km2'])} million km²).
- Frontiers: the Brazilian Cerrado went from {HS['cerrado']['farm_1900_pct']:.0f}% farmed to {HS['cerrado']['farm_2023_pct']:.0f}%, the Sahel from {HS['sahel']['farm_1900_pct']:.0f}% to {HS['sahel']['farm_2023_pct']:.0f}%, Southeast Asia from {HS['se_asia']['farm_1900_pct']:.0f}% to {HS['se_asia']['farm_2023_pct']:.0f}%; the US Midwest was already {HS['midwest']['farm_1900_pct']:.0f}% farmed in 1900.
- Forest zone: the farmed share of land where forest is the natural vegetation rose from {F['cleared_1900_pct']:.1f}% to {F['cleared_2023_pct']:.1f}% (net +{m(F['net_km2'])} million km²; gross +{m(F['gross_gain_km2'])}, -{m(F['gross_loss_km2'])}). {CH['gross_loss_share_us_europe_russia_pct']:.0f}% of the land that left farming is in Europe, Russia and the United States; east of 90°W in the US the farmed share fell from {CH['east_us']['c1900_pct']:.0f}% to {CH['east_us']['c2023_pct']:.0f}%.
- Anthromes: used land (settlements, villages, croplands, rangelands) rose from {AN['used_1900_pct']:.0f}% to {AN['used_2023_pct']:.0f}% of ice-free land; wildlands barely changed ({AN['wild_1900_pct']:.0f}% to {AN['wild_2023_pct']:.0f}%), while seminatural lands fell from {AN['semi_1900_pct']:.0f}% to {AN['semi_2023_pct']:.0f}%.
- Satellite check (MODIS 2019): forest or woody savanna on {MO['treecover_in_zone_pct']:.0f}% of the forest zone, against {F['uncleared_2023_pct']:.0f}% unfarmed in HYDE; MODIS cropland is {MO['crop_vs_hyde_pct']:.0f}% of HYDE's.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, grids loaded from `data/page/`). |
| `header.png` | Social card, 1200 x 630. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/country_landuse_1900_2023.csv` | Every HYDE country: land, ice, forest zone, cropland, grazing land, pasture, farmland, farmed forest zone, wildlands and dense settlements in 1900 and 2023 (km²), shares and changes. |
| `data/region_landuse_1900_2023.csv` | The same for twelve world regions. |
| `data/hyde32_world_1700_2016.csv` | World cropland, grazing land and built-up area 1700 to 2016 from HYDE 3.2 (via Our World in Data), km². |
| `data/hyde33_10arcmin_1900_2023.tif` | GeoTIFF, 10 arc-minutes: land, cropland, grazing, pasture and farmed forest zone in 1900 and 2023 (km²), forest zone, and anthromes ({sz('data/hyde33_10arcmin_1900_2023.tif')}). |
| `data/page/g1.png` to `g5.png` | Page grids, PNG-encoded (documented in `code/04_page_data.py`). |
| `data/site.json`, `data/world.json`, `data/countries_geo.json`, `data/cities.json` | Page data and Natural Earth geometry. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures, blog post with figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots of the page at desktop and phone widths. |

## Method in brief

- Farmland: HYDE 3.3 baseline cropland + pasture + rangeland + converted rangeland (km² per 5 arc-minute cell). Shares are of HYDE's maximum land area; ice-free land removes cells of the anthrome 'ice, uninhabited'.
- Forest zone: HYDE's potential forest file (WWF biomes). Farmed = cropland + pasture + converted rangeland inside it. This measures farming, not forest cover: logging, fire and plantations do not show.
- Countries and regions from HYDE's country grid matched to Natural Earth; twelve regions from Natural Earth subregions with Russia on its own; eleven named boxes for hotspots (listed in the paper).
- Anthromes: HYDE's own 1900 and 2023 anthrome maps (Ellis et al. classes).
- MODIS: MCD12C1 v006 2019 IGBP classes, compared with HYDE on a quarter-degree grid.
- Long series: HYDE 3.2 world totals, because only the 1900 and 2023 HYDE 3.3 slices are used.
- Caveats: the 1900 map is a model from historical statistics and allocation rules; trust totals more than single cells, and Africa, Asia and Latin America least. Grazing land is mostly natural rangeland.

## How to rerun

Needs Python 3 with numpy, pandas, rasterio, shapely, pyproj, matplotlib, fontTools, openpyxl and Pillow, plus xelatex and pdftotext; node with Playwright for the screenshots. Raw inputs are read from the paths in `code/common.py`: the HYDE 3.3 baseline zips `1900AD_lu`, `2023AD_lu`, `1900AD_anthromes`, `2023AD_anthromes` and `general_files` (Utrecht University data vault, DOI 10.24416/UU01-94FNH0), the MCD12C1 2019 GeoTIFF from the `MCD12C1-2019-v006` package on GitHub, `Land Use Data - HYDE (2017).csv` from `owid/owid-datasets` on GitHub, and Natural Earth 1:50m countries and 1:10m populated places.

```
python3 code/01_load_grids.py   # HYDE ASCII grids and MODIS to arrays (outside the repo)
python3 code/02_geo.py          # world outlines and cities
python3 code/03_analysis.py     # results.json and CSVs
python3 code/04_page_data.py    # page PNG grids, site.json, GeoTIFF
python3 code/05_build_site.py   # index.html (and checks of facts stated in words)
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/08_readme.py       # README and LICENSE
python3 code/09_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
node code/qa_shots.js           # screenshots to qa/
```

## Sources and licences

- HYDE 3.3: Klein Goldewijk, K., Beusen, A., Doelman, J. and Stehfest, E. History Database of the Global Environment 3.3. Utrecht University. https://doi.org/10.24416/UU01-94FNH0. CC BY 4.0. Method: Klein Goldewijk et al. (2017) Anthropogenic land use estimates for the Holocene: HYDE 3.2. Earth System Science Data 9, 927 to 953.
- HYDE 3.2 world totals as republished by Our World in Data (owid-datasets, CC BY 4.0).
- Anthromes: Ellis et al. (2010, 2021), as implemented in HYDE.
- MODIS MCD12C1 v006: Friedl, M. and Sulla-Menashe, D., NASA LP DAAC, https://doi.org/10.5067/MODIS/MCD12C1.006 (public domain).
- Natural Earth (public domain). Base map tiles on the page: © Esri.

Code is MIT; text, figures and derived data are CC BY 4.0 (see LICENSE).

## Citation

Hotham, T. (2026) Desert, forest, ice: the world's land in 1900 and now, from HYDE 3.3. Zenodo. {doi}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in md.replace("```", "").replace("|---|---|", ""), (bad, md[max(0, md.find(bad) - 80):md.find(bad) + 20])
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(md)
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data (everything outside code/): Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
Derived from HYDE 3.3 (Klein Goldewijk et al., Utrecht University, CC BY 4.0) and HYDE 3.2 world totals via Our World in Data (CC BY 4.0). MODIS MCD12C1 (NASA) and Natural Earth data are public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(md.split()), "words")
