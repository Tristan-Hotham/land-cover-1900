"""Build the paper: fill code/paper_template.tex from data/results.json, add the region and hotspot tables, compile with
xelatex. Output: release/paper/Hotham_Desert_Forest_Ice.pdf and .tex (figures release/paper/f_*.png)."""
import re, subprocess
import pandas as pd
from common import *
import importlib.util
spec_ = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py")); spec_.loader.exec_module(importlib.util.module_from_spec(spec_))  # runs the shared asserts

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Desert_Forest_Ice"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
# facts stated only in the paper
H = R["hyde"]; HS = R["change"]["hotspots"]
assert HS["midwest"]["crop_2023_pct"] < HS["midwest"]["crop_1900_pct"]
assert R["anthromes"]["wildwood_chg_pct"] < 0 and all(r["farm_chg_km2"] > 0 for r in R["regions"] if r["name"] != "Europe")
assert R["anthromes"]["ice_2023_km2"] == H["ice_2023_km2"]


def pfmt(v, f):
    s = fmt(v, f) if f else tex(v)
    return s.replace("%", "\\%")


rg = pd.read_csv(f"{DATA}/region_landuse_1900_2023.csv")
body = "".join(f"{r.region} & {(r.land_km2 - r.ice_km2) / 1e6:.1f} & {r.farm_1900_km2 / 1e6:.2f} & {r.farm_2023_km2 / 1e6:.2f} & {r.farm_1900_pct:.0f} & {r.farm_2023_pct:.0f} & "
               f"{(100 * r.cleared_1900_km2 / r.forest_zone_km2) if r.forest_zone_km2 > 0 else 0:.0f} & {(100 * r.cleared_2023_km2 / r.forest_zone_km2) if r.forest_zone_km2 > 0 else 0:.0f}\\\\\n"
               for r in rg.itertuples())
TR = ("\\begin{table}[tbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\\caption{Farmland by region, 1900 and 2023: ice-free land (million km\\textsuperscript{2}), farmland (million km\\textsuperscript{2}), "
      "farmland as a share of ice-free land (\\%), and the farmed share of the forest zone (\\%). HYDE 3.3 baseline.}\\label{tab:reg}"
      "\\begin{tabular}{lrrrrrrr}\\toprule Region & Land & Farm 1900 & Farm 2023 & \\% 1900 & \\% 2023 & Forest zone 1900 & 2023\\\\\\midrule\n" + body + "\\bottomrule\\end{tabular}\\end{table}")
hb = "".join(f"{h['name']} & {h['box'][0]} to {h['box'][1]} & {h['box'][2]} to {h['box'][3]} & {h['farm_1900_pct']:.0f} & {h['farm_2023_pct']:.0f} & {h['crop_1900_pct']:.0f} & {h['crop_2023_pct']:.0f}\\\\\n" for h in HS.values())
TH = ("\\begin{table}[tbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\\caption{Named boxes: latitude and longitude limits, and farmland and cropland as a share of their land (\\%), 1900 and 2023. "
      "Boxes named after a country are limited to that country.}\\label{tab:hot}"
      "\\begin{tabular}{lrrrrrr}\\toprule Region & Latitude & Longitude & Farm 1900 & Farm 2023 & Crop 1900 & Crop 2023\\\\\\midrule\n" + hb + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{meta_page}}", PAGE).replace("{{meta_repo}}", REPO)
t = fill(t, R, pfmt, skip=("TABLE_", "DOI"))
t = t.replace("{{TABLE_REG}}", TR).replace("{{TABLE_HOT}}", TH).replace("10.5281/zenodo.23847971", DOI)
assert not re.search(r"\{\{(?!DOI\}\})", t), re.findall(r"\{\{[^}]*\}\}", t)[:5]
for bad in ("--", "—", "–", "DSIT", "DCMS"):
    assert bad not in t, bad
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
