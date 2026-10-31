"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; results and present-day city names are embedded; data/site.json, data/maps/<year>.json, flag images
and data/borders_today.json are loaded by the page. Facts stated in words are checked here against the data.
The full-screen map snippet (from the drinks-map reference, code/fullscreen_snippet.html) goes before </body>.
{{DOI}}, {{DOI_URL}} and {{BLOG_URL}} are left for the publisher to fill."""
from common import *

R = jload(f"{DATA}/results.json")
SN = jload(f"{WORK}/snaps_owned.json")
EM = jload(f"{WORK}/emblems.json")
cy = {c["y"]: c for c in R["cover"]}
city = {c["c"]: c for c in R["cities"]}

# facts stated in words (page; the blog and paper reuse them)
assert cy[1000]["flag"] == 0 and cy[1000]["arms"] == 0
assert EM["Holy Roman Empire|1200"]["kind"] == "flag" and EM["Venice|1200"]["kind"] == "flag"
assert EM["Qing Empire|1880"]["file"].startswith("Flag of China (1862")
assert EM["United Kingdom|1815"]["file"] == "Flag of the United Kingdom (3-5).svg" and EM["United Kingdom|1800"]["file"].startswith("Flag of Great Britain (1707")
assert R["largest_ever"]["n"] == "Mongol Empire"
# "largest single entry in the basemap": no single holder in any snapshot is larger
assert all(e["top"][0]["a"] <= R["largest_ever"]["a"] for e in R["entities"]) and R["largest_ever"]["a"] > R["russia_peak"]["a"] > R["uk_peak"]["a"]
# "the British Empire with colonies and dominions was larger"
assert R["uk_dom_peak"]["pct"] > R["largest_ever"]["pct"] and R["uk_dom_peak"]["y"] == 1914 and R["uk_dom_peak"]["a"] > R["largest_ever"]["a"]
assert all(r["n"] in ("Tsardom of Muscovy", "Russian Empire", "Russia", "USSR") for r in R["largest_by_year"] if r["y"] >= 1600)
b = [h["o"] for h in city["Boston"]["h"]]
assert all(o == "Eastern North American hunter-gatherers" for o in b[:8]) and "Massachusett" in b[8] and b[9] == "Iroquois" and b[10] == "Massachusett"
assert b[12] == "England" and R["years"][12] == 1650 and b[14] == "United Kingdom" and R["years"][14] == 1715 and b[15] == "United States" and R["years"][15] == 1783
assert EM["United Kingdom|1715"]["file"].startswith("Flag of Great Britain")
bj = [h["o"] for h in city["Beijing"]["h"]]
seq = [o for i, o in enumerate(bj) if i == 0 or o != bj[i - 1]]
assert seq == ["Tang Empire", "Liao", "Mongol Empire", "Ming Empire", "Qing Empire", "Chinese Warlords", "China"], seq
assert EM["China|1945"]["file"] == "Flag of the Republic of China.svg" and EM["China|1960"]["file"] == "Flag of the People's Republic of China.svg"
assert R["euro"][[d["y"] for d in R["euro"]].index(1815)]["overseas"] > R["euro"][[d["y"] for d in R["euro"]].index(1878)]["overseas"]
own60 = {f["NAME"]: f["owner"] for f in SN["1960"]}
assert own60.get("Angola") == "Angola" and own60.get("Mozambique") == "Mozambique"
assert R["entities"][8]["y"] == 1492 and R["euro_1492"]["y"] == 1492 and R["cover"][8]["y"] == 1492
fa = R["flag_age"]
assert [o["country"] for o in fa["oldest"][:3]] == ["United Kingdom", "Netherlands", "Norway"]
import csv
ages = {r["country"]: r for r in csv.DictReader(open(f"{DATA}/flag_age.csv", encoding="utf-8"))}
assert ages["Japan"]["adopted"] == "1999" and ages["Italy"]["adopted"] == "2006" and ages["France"]["adopted"] == "2020" and ages["Denmark"]["adopted"] == ""
assert EM["USSR|1920"]["kind"] == "plain" and cy[1920]["flag"] < cy[1914]["flag"] and cy[1920]["flag"] < cy[1930]["flag"]
assert R["fixes"] == 2 and R["states_max"]["y"] == 1994


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl, R)
    assert not re.search(r"\{\{(?!DOI\}\}|DOI_URL\}\}|BLOG_URL\}\})", html), re.findall(r"\{\{[^}]*\}\}", html)[:5]
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*CITIES*/", open(f"{DATA}/cities.json", encoding="utf-8").read())
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    check_dashes(vis, "page text")
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    for bad in ("DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in html, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
