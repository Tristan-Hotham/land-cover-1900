"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo), Reddit post text (reddit/post.md).
Zenodo copies of files that also live elsewhere in the repo are hard links."""
import re, zipfile, json as _json
from common import *
import importlib.util
spec_ = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py")); spec_.loader.exec_module(importlib.util.module_from_spec(spec_))  # shared asserts

R = jload(f"{DATA}/results.json"); H, AN, S0 = R["hyde"], R["anthromes"], R["series"]
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Desert_Forest_Ice"
# facts in the blog alt text and prose
assert [round(r["farm_chg_km2"] / 1e6, 1) for r in R["regions"]] == [5.7, 4.7, 2.5, 2.4, 2.1, 1.6, 1.2, 1.2, 1.2, 0.9, 0.5, -0.4]
assert round(S0["farm_1700_km2"] / 1e6) == 10 and round(S0["farm_1900_v32_km2"] / 1e6) == 25 and 47 <= (S0["farm_1950_km2"] + S0["farm_1950_1990_gain_km2"]) / 1e6 <= 49
assert [round(AN[k]) for k in ("range_1900_pct", "range_2023_pct", "crop_1900_pct", "crop_2023_pct", "village_1900_pct", "village_2023_pct", "semi_1900_pct", "semi_2023_pct", "wild_1900_pct", "wild_2023_pct")] == [22, 28, 10, 15, 3, 8, 40, 24, 25, 24]
assert all(x["v"] > 2e6 for x in R["change"]["top_farm_gain"][:3])
DOI_URL = "https://doi.org/" + DOI if not DOI.startswith("{{") else "https://doi.org/10.5281/zenodo.23847971"

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R).replace("https://doi.org/10.5281/zenodo.23847971", DOI_URL)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
for ln in post.splitlines():                                   # IMG tokens on their own lines, outside image blocks
    if "{{IMG|" in ln: assert ln.startswith("{{IMG|") and ln.endswith("}}"), ln[:60]
assert "wp:image" not in post
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
assert not re.search(r"\{\{(?!IMG\||DOI_URL\}\})", post)
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Desert, forest, ice: the world in 1900 and now",
        "slug": "land-cover-1900",
        "excerpt": f"In 1900 farms covered {H['farm_1900_pct']:.0f}% of the world's ice-free land. Today they cover {H['farm_2023_pct']:.0f}%. Two maps from HYDE 3.3 show where the new fields and pastures came from, which forests went, and where the trees came back.",
        "seo_description": f"The world's land in 1900 and now: farmland grew from {H['farm_1900_pct']:.0f}% to {H['farm_2023_pct']:.0f}% of ice-free land. Swipe map of cropland, grazing, forest and wildlands.",
        "tags": ["land use", "history", "farming", "deforestation", "forests", "maps", "data visualisation", "HYDE"],
        "header_alt": f"Title card reading 'Desert, forest, ice' in gold, green and pale blue on cream, beside two world maps of farmland in 1900 and 2023 shaded from cream to dark brown. Text: farms covered {H['farm_1900_pct']:.0f}% of the world's ice-free land in 1900; today {H['farm_2023_pct']:.0f}%."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst): os.remove(dst)
    os.link(src, dst)


link(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/land-cover-1900_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "data/page", "reddit"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isdir(p) or fn.endswith(".pyc") or fn.endswith(".png") and d == "reddit":
                continue
            z.write(p, f"land-cover-1900/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"land-cover-1900/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("km\\textsuperscript{2}", "km²")
assert "\\" not in ab, ab[ab.find("\\") - 30:ab.find("\\") + 30]
zmeta = {"metadata": {
    "title": "Desert, Forest, Ice: the World's Land in 1900 and Now, from HYDE 3.3",
    "upload_type": "publication", "publication_type": "workingpaper",
    "description": f"<p>{ab}</p><p>Interactive version: {PAGE}. Data and code: {REPO}.</p>",
    "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
    "keywords": ["land use", "land cover", "HYDE", "anthromes", "deforestation", "reforestation", "farmland", "historical geography", "maps"],
    "license": "cc-by-4.0", "access_right": "open", "language": "eng",
    "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                            {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                            {"identifier": "10.24416/UU01-94FNH0", "relation": "isDerivedFrom", "resource_type": "dataset"},
                            {"identifier": "10.5067/MODIS/MCD12C1.006", "relation": "isDerivedFrom", "resource_type": "dataset"},
                            {"identifier": "10.5194/essd-9-927-2017", "relation": "references", "resource_type": "publication-article"},
                            {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
    "notes": AI},
    "files": [f"{NAME}.pdf", "land-cover-1900_code_and_data.zip"]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)

# Reddit post
CH = R["change"]
md = f"""# Reddit post

**Subreddit:** r/dataisbeautiful

**Title:** [OC] In 1900 farms covered {H['farm_1900_pct']:.0f}% of the world's ice-free land. Today they cover {H['farm_2023_pct']:.0f}%: cropland and grazing land, 1900 vs 2023

**Image:** `world_farmland_1900_2023.png`

**Body:**

Two maps from HYDE 3.3, the historical land use reconstruction from Utrecht University, showing the share of every 9 km square used for crops or grazing in 1900 and in 2023.

- Farmland grew by {H['farm_gain_km2'] / 1e6:.1f} million km², {H['farm_gain_vs_us']:.1f} times the area of the US. Most of it is grazing on natural rangeland.
- The frontier moved into the tropics and drylands: the Brazilian Cerrado went from {CH['hotspots']['cerrado']['farm_1900_pct']:.0f}% farmed to {CH['hotspots']['cerrado']['farm_2023_pct']:.0f}%, the Sahel from {CH['hotspots']['sahel']['farm_1900_pct']:.0f}% to {CH['hotspots']['sahel']['farm_2023_pct']:.0f}%.
- Europe is the only region with less farmland than in 1900, and in the eastern US much of the old farmland grew back to woods.

The 1900 map is a model built from historical statistics, so trust the big picture more than single squares. Interactive swipe map (cropland, grazing, forest zone, anthromes, 2019 satellite land cover): {PAGE}

**Source comment:**

Data: HYDE 3.3 baseline (Klein Goldewijk et al., Utrecht University, CC BY 4.0, doi:10.24416/UU01-94FNH0) for 1900 and 2023 at 5 arc-minutes; world series 1700 to 2016 from HYDE 3.2 via Our World in Data; outlines Natural Earth. Farmland = cropland + pasture + rangeland + converted rangeland; ice-free land excludes Antarctica and the Greenland ice sheet. Tools: Python (numpy, rasterio, matplotlib), Equal Earth projection. Paper, data and code: {PAGE}
"""
for bad in ("\u2014", "\u2013", "--"):
    assert bad not in md, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(md)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
