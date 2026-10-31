"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, world.json, cities) is embedded and data/page/*.png are loaded by the page.
Facts stated in words are checked here (the blog and paper builds import this module for the same checks). The full-screen
map snippet (code/fullscreen_snippet.html, from the reference studies) is pasted before </body>."""
import json, re
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
H, F, AN, CH = R["hyde"], R["forest"], R["anthromes"], R["change"]
HS = CH["hotspots"]
cdf = pd.read_csv(f"{DATA}/country_landuse_1900_2023.csv", keep_default_na=False)
crow = lambda i: cdf[cdf.iso3 == i].iloc[0]
isos = lambda L: [x["iso"] for x in L]

# ---- facts stated in words (page, blog, paper, collage) ----
assert [r["name"] for r in R["regions"][:4]] == ["Sub-Saharan Africa", "South America", "East Asia", "Oceania"]
assert [r["name"] for r in R["regions"] if r["farm_chg_km2"] < 0] == ["Europe"]                       # "only Europe has less"
assert isos(CH["top_farm_gain"][:6]) == ["CHN", "BRA", "AUS", "USA", "ARG", "KAZ"]
assert isos(CH["top_clear_gain"][:5]) == ["BRA", "CHN", "IDN", "AUS", "IND"]
assert isos(CH["top_clear_loss"][:4]) == ["FRA", "POL", "ITA", "DEU"]
assert isos(CH["top_farm_loss"][:4]) == ["FRA", "POL", "ITA", "DEU"]
for i in ("AUS", "CHN"):                                                                               # "mostly new grazing land"
    r = crow(i); assert (r.graz_2023_km2 - r.graz_1900_km2) > 0.65 * r.farm_chg_km2
assert CH["BRA"]["cleared_chg_km2"] > 0.4 * CH["BRA"]["farm_chg_km2"]                                # "much of it was clearing"
se = HS["se_asia"]; assert se["crop_chg_km2"] > 0.8 * se["farm_chg_km2"]                             # "it was cropland"
assert abs(HS["midwest"]["farm_2023_pct"] - HS["midwest"]["farm_1900_pct"]) < 3                       # "already there in 1900"
assert HS["cerrado"]["farm_1900_pct"] < 5 and float(crow("IDN")["cleared_1900_pct_of_zone"]) < 20             # open savanna; forests largely intact
assert HS["europe_w"]["farm_2023_pct"] < HS["europe_w"]["farm_1900_pct"]                               # "farmed harder than it is today"
assert AN["wild1900_to"]["wild"] > 90 and abs(AN["wild_1900_pct"] - AN["wild_2023_pct"]) < 2          # "the wildlands barely moved"
assert AN["semi_1900_pct"] - AN["semi_2023_pct"] > 10
assert R["modis"]["treecover_in_zone_pct"] < F["uncleared_2023_pct"] and R["modis"]["forest_in_zone_pct"] < R["modis"]["treecover_in_zone_pct"]
assert CH["gross_loss_share_us_europe_russia_pct"] > 75 and CH["east_us"]["net_km2"] < 0 and CH["europe"]["farm_chg_km2"] < 0
assert R["series"]["farm_1990_2016_gain_km2"] < R["series"]["farm_1950_1990_gain_km2"] / 4             # "far more slowly"
assert R["series"]["farm_1900_1950_gain_km2"] > 0.8 * R["series"]["farm_1700_1900_gain_km2"]
assert R["uk"]["crop_2023_km2"] < R["uk"]["crop_1900_km2"] and abs(R["uk"]["farm_2023_pct"] - R["uk"]["farm_1900_pct"]) < 10
assert 2.4 < H["farm_gain_vs_us"] < 2.7


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R).replace("10.5281/zenodo.23847971", DOI).replace("https://blog.tristanhotham.com/2026/10/31/land-cover-1900/", BLOG)
    assert not re.search(r"\{\{(?!DOI\}\}|BLOG_URL\}\})", html), re.findall(r"\{\{[^}]*\}\}", html)[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
