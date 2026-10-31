"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
{{DOI}}, {{DOI_URL}} and {{BLOG_URL}} are left for the publisher to fill."""
import shutil, zipfile, json as _json
from common import *

R = jload(f"{DATA}/results.json")
EM = jload(f"{WORK}/emblems.json")
REL = os.path.join(ROOT, "release")
NAME = "Hotham_Who_Held_the_Map"

# facts written out in words in the blog and paper, checked here (the page build checks the rest)
import importlib.util
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "06_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
lb = {r["y"]: r["n"] for r in R["largest_by_year"]}
assert lb[800] == lb[900] == "Abbasid Caliphate" and all(lb[y] == "Mongol Empire" for y in (1200, 1279, 1300, 1400))
assert [b["n"] for b in R["flag_age"]["bins"] if b["b"] in (1960, 1980, 2000)] == [21, 26, 22]
assert all(EM[f"Ottoman Empire|{y}"]["kind"] == "plain" for y in (1400, 1500, 1600, 1815)) and EM["Ottoman Empire|1878"]["file"].startswith("Flag of the Ottoman Empire (1844")
assert EM["Tsardom of Muscovy|1530"]["kind"] == "plain" and EM["Mongol Empire|1279"]["kind"] == "plain"
assert R["most_owners_city"]["c"] == "Moscow" and R["first_flag_half"] == 1878 and round(R["flag_share_2010"]) == 97
assert EM["Holy Roman Empire|1600"]["kind"] == "flag" and EM["Spain|1600"]["file"] == "Flag of Cross of Burgundy.svg" and EM["Ottoman Empire|1600"]["kind"] == "plain"

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
check_dashes(vis, "blog")
assert AI in post
for bad in ("DSIT", "DCMS", "civil serv"):
    assert bad not in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Who held the map? Twelve centuries of the world in flags",
        "slug": "flags-through-time",
        "excerpt": f"The world map from 800 to 2010, each piece of land filled with the flag of whoever held it. In 1000 no land can honestly be shown with a flag; in 1500, {R['flag_share_1500']:.1f}%; by 2010, {R['flag_share_2010']:.0f}%.",
        "seo_description": "An interactive world map in flags from 800 to 2010: who held each piece of land, its flag at the time, and where no flag can honestly be drawn.",
        "tags": ["flags", "history", "empires", "maps", "data visualisation", "Wikidata", "vexillology"],
        "header_alt": f"Title card reading 'Who held the map?' in black on cream, beside a world map of 1914 in which each area is filled with its holder's flag: the Union Flag across Canada, India and much of Africa, the Russian tricolour across Russia, the Stars and Stripes, Brazil's green and gold. Text: {R['flag_share_1500']:.1f}% of land under a flag in 1500, {R['flag_share_2010']:.0f}% in 2010."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/flags-through-time_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "data/maps", "data/flags"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isdir(p) or fn.endswith(".pyc"):
                continue
            z.write(p, f"flags-through-time/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"flags-through-time/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\citep{ourednik}", "(Ourednik and contributors)").replace("\\%", "%").replace("\\&", "&")
assert "\\" not in ab, ab
zmeta = {"title": "Who Held the Map? Twelve Centuries of the World in Flags, 800 to 2010, from Historical Basemaps and Wikidata",
         "upload_type": "publication", "publication_type": "workingpaper",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{URL}\">{URL}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p>"
                        "<p>Licences: the paper (text and figures) is CC BY-SA 4.0, because the figures include flag images released under CC BY-SA. "
                        "The simplified boundaries and area tables in the zip (data/maps, data/areas.csv) derive from historical-basemaps and are GPL-3.0. "
                        "Flag images keep their own licences, listed in data/flag_credits.csv. Code is MIT.</p>"
                        f"<p>{AI}</p>",
         "keywords": ["flags", "vexillology", "historical maps", "empires", "colonialism", "Wikidata", "historical GIS", "maps", "open data"],
         "license": "cc-by-sa-4.0",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": URL, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://github.com/aourednik/historical-basemaps", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://commons.wikimedia.org/", "relation": "isDerivedFrom", "resource_type": "image"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
check_dashes(s, "metadata")
print("blog words", words, "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
