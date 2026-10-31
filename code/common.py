"""Shared paths and helpers for the land-cover-1900 project. Raw inputs are read in place (paths below); intermediates
live in memory (/dev/shm), not in the repo."""
import json, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW3 = "/home/claude/newdata/raw3"
# HYDE 3.3 baseline (hyde33_c7_base_mrt2023), ESRI ASCII grids at 5 arc-minutes, km2 per cell, from the Utrecht University
# data vault (DOI 10.24416/UU01-94FNH0): 1900AD_lu.zip, 2023AD_lu.zip, 1900AD_anthromes.zip, 2023AD_anthromes.zip,
# general_files.zip, unzipped in place.
RAW_GRID = f"{RAW3}/grid"
GEN = f"{RAW_GRID}/general_files/general_files"
COUNTRY_CODES = f"{RAW_GRID}/general_files/HYDE_country_codes.xlsx"
HYDE_DOI = "10.24416/UU01-94FNH0"
YEARS = (1900, 2023)
# HYDE 3.2 regional series 1700 to 2016 (Our World in Data's GitHub copy, owid/owid-datasets), for the long time series only
OWID_HYDE32 = f"{RAW3}/owid-datasets/datasets/Land Use Data - HYDE (2017)/Land Use Data - HYDE (2017).csv"
# MODIS MCD12C1 v006 2019 land cover, IGBP majority class at 0.05 degrees (GitHub: JPL-Evapotranspiration-Algorithms/MCD12C1-2019-v006)
MODIS = f"{RAW3}/mcd12c1/MCD12C1_2019_v006/MCD12C1.A2019001.006.2020220162300.tif"
GEO = "/home/claude/newdata/raw/geo"
NE50 = f"{GEO}/ne_50m_admin_0_countries.geojson"
NEPLACES = f"{GEO}/ne_10m_populated_places_simple.geojson"
DATA = os.path.join(ROOT, "data")
PAGE_D = os.path.join(DATA, "page")
SHM = os.environ.get("LCTMP", "/home/claude/newdata/work/land-cover-1900")   # intermediates (outside the repo)
WORK = SHM
for d in (DATA, PAGE_D, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "land-cover-1900"
TITLE = "Desert, forest, ice: the world in 1900 and now"
PAGE = "https://maps.tristanhotham.com/land-cover-1900/"
REPO = "https://github.com/Tristan-Hotham/land-cover-1900"
DOI = os.environ.get("LC_DOI", "10.5281/zenodo.23847971")            # set LC_DOI=10.5281/zenodo.N and rerun the build scripts to fill it in
BLOG = os.environ.get("LC_BLOG", "https://blog.tristanhotham.com/2026/10/31/land-cover-1900/")
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# HYDE 3.3 anthromes (Ellis et al. scheme): code, name, group
ANTH = [(11, "Urban", "settle"), (12, "Mixed settlements", "settle"), (21, "Rice villages", "village"),
        (22, "Irrigated villages", "village"), (23, "Rainfed villages", "village"), (24, "Pastoral villages", "village"),
        (31, "Residential irrigated croplands", "crop"), (32, "Residential rainfed croplands", "crop"),
        (33, "Populated croplands", "crop"), (34, "Remote croplands", "crop"), (41, "Residential rangelands", "range"),
        (42, "Populated rangelands", "range"), (43, "Remote rangelands", "range"), (51, "Residential woodlands", "semi"),
        (52, "Populated woodlands", "semi"), (53, "Remote woodlands", "semi"), (54, "Inhabited drylands", "semi"),
        (61, "Wild woodlands", "wild"), (62, "Wild drylands", "wild"), (63, "Ice, uninhabited", "ice")]
AGROUP = [("settle", "Dense settlements", "#5B4B66"), ("village", "Villages", "#B5562E"), ("crop", "Croplands", "#D9A33B"),
          ("range", "Rangelands", "#B8C27A"), ("semi", "Seminatural lands", "#6E9E6A"), ("wild", "Wildlands", "#2F5D4A"),
          ("ice", "Ice", "#CFE3EA")]
COL = {"crop": "#D9A33B", "graz": "#9DB46C", "past": "#6F9A3E", "range": "#C9CF9A", "urban": "#5B4B66",
       "forest": "#2F6B4F", "cleared": "#B5562E", "regrow": "#2E7D6B", "gain": "#B5562E", "loss": "#2E7D6B"}


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jsave(obj, path, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def results_update(section, d):
    p = os.path.join(DATA, "results.json")
    r = jload(p) if os.path.exists(p) else {}
    r[section] = d
    jsave(r, p, indent=1)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    """Template formats: int, pc (rounded per cent), pc1, f1, f2, m1 (millions, 1 dp), m0, signed1, abs1, raw."""
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "m1": return f"{float(v) / 1e6:,.1f}"
    if f == "m0": return f"{float(v) / 1e6:,.0f}"
    if f == "am1": return f"{abs(float(v)) / 1e6:,.1f}"
    if f == "abs1": return f"{abs(float(v)):.1f}"
    if f == "absint": return f"{abs(round(float(v))):,}"
    if f == "x1": return f"{float(v):.1f}"
    raise ValueError(f)


def fill(text, R, fmtfun=fmt, skip=("IMG", "DOI", "BLOG_URL")):
    pat = r"\{\{(?!" + "|".join(skip) + r")([^}|]+)(\|(\w+))?\}\}"
    return re.sub(pat, lambda m: fmtfun(get(R, m.group(1)), m.group(3)), text)
