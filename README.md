# Desert, forest, ice: the world in 1900 and now

The world's land in 1900 and 2023 on one swipe map: cropland, grazing land, farming in the natural forest zone, anthromes (wild, seminatural and used land) and present-day satellite land cover. Built from the HYDE 3.3 historical land use reconstruction (5 arc-minute grids) and MODIS MCD12C1 land cover for 2019.

Interactive page: https://maps.tristanhotham.com/land-cover-1900/
Paper: https://doi.org/10.5281/zenodo.23847971
Blog post: https://blog.tristanhotham.com/2026/10/31/land-cover-1900/

## Headline results

- Farmland (cropland plus grazing land) covered 19.1% of the world's ice-free land in 1900 and 37.3% in 2023 (HYDE 3.3 baseline; Antarctica excluded). Cropland grew from 9.0 to 16.3 million km², grazing land from 15.7 to 32.0 million km². The net gain, 23.5 million km², is 2.6 times the area of the United States.
- Where: the largest gains were in sub-Saharan Africa (+5.7 million km²) and South America (+4.7); by country China, Brazil and Australia (each more than 2 million km²). Europe is the only region with less farmland than in 1900 (-0.4 million km²).
- Frontiers: the Brazilian Cerrado went from 3% farmed to 41%, the Sahel from 26% to 64%, Southeast Asia from 12% to 37%; the US Midwest was already 50% farmed in 1900.
- Forest zone: the farmed share of land where forest is the natural vegetation rose from 16.4% to 27.3% (net +6.4 million km²; gross +7.6, -1.2). 87% of the land that left farming is in Europe, Russia and the United States; east of 90°W in the US the farmed share fell from 38% to 31%.
- Anthromes: used land (settlements, villages, croplands, rangelands) rose from 35% to 52% of ice-free land; wildlands barely changed (25% to 24%), while seminatural lands fell from 40% to 24%.
- Satellite check (MODIS 2019): forest or woody savanna on 53% of the forest zone, against 73% unfarmed in HYDE; MODIS cropland is 80% of HYDE's.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, grids loaded from `data/page/`). |
| `header.png` | Social card, 1200 x 630. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/country_landuse_1900_2023.csv` | Every HYDE country: land, ice, forest zone, cropland, grazing land, pasture, farmland, farmed forest zone, wildlands and dense settlements in 1900 and 2023 (km²), shares and changes. |
| `data/region_landuse_1900_2023.csv` | The same for twelve world regions. |
| `data/hyde32_world_1700_2016.csv` | World cropland, grazing land and built-up area 1700 to 2016 from HYDE 3.2 (via Our World in Data), km². |
| `data/hyde33_10arcmin_1900_2023.tif` | GeoTIFF, 10 arc-minutes: land, cropland, grazing, pasture and farmed forest zone in 1900 and 2023 (km²), forest zone, and anthromes (11.6 MB). |
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

Hotham, T. (2026) Desert, forest, ice: the world's land in 1900 and now, from HYDE 3.3. Zenodo. https://doi.org/10.5281/zenodo.23847971

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
