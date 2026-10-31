"""Web geometry: one simplified TopoJSON per snapshot (data/maps/<year>.json, loaded by the page when that year is shown),
with each area's name (NAME), owner (an index into the owner table in data/site.json), border precision, land area
and label point. Simplified with mapshaper (Visvalingam, 20% of points kept, shapes kept), coordinates quantised.
Also data/areas.csv (every area in every snapshot with its owner and emblem) and data/site.json (page tables)."""
import csv, subprocess, hashlib, urllib.parse
from common import *

SN = jload(f"{WORK}/snaps_owned.json")
OW = jload(f"{WORK}/owners.json")
EM = jload(f"{WORK}/emblems.json")
FM = jload(f"{WORK}/flagmeta.json")
IT = jload(f"{WORK}/items.json")
names = sorted(OW, key=lambda o: -sum(OW[o]["years"].values()))
OID = {o: i for i, o in enumerate(names)}
PAL = ["#C9A27E", "#A7B48C", "#D8B26E", "#9FB7B0", "#C99A9A", "#B5A6C9", "#D6C08E", "#93A9C4", "#C7B39B", "#A9C3A0", "#CFA7B9", "#B9B08A"]


def plain_col(o):
    return PAL[int(hashlib.md5(o.encode()).hexdigest(), 16) % len(PAL)]


hb = jload(f"{HB}/geojson/world_2010.geojson")   # just to confirm the raw path exists
for y in YEARS:
    raw = jload(f"{HB}/geojson/world_{y}.geojson")["features"]
    feats = []
    for f in SN[str(y)]:
        g = raw[f["i"]]["geometry"]
        o = f["owner"]
        feats.append({"type": "Feature", "geometry": g, "properties": {
            "n": f["NAME"] or "", "o": OID[o] if o else -1, "b": f["BP"] or 1, "a": round(f["area"]), "lx": f["pt"][0], "ly": f["pt"][1]}})
    src = f"{WORK}/geo_{y}.json"
    jsave({"type": "FeatureCollection", "features": feats}, src)
    out = f"{MAPS}/{y}.json"
    r = subprocess.run(["mapshaper", "-i", src, "-simplify", "percentage=20%", "weighted", "keep-shapes",
                        "-o", out, "format=topojson", "quantization=40000", "force"], capture_output=True, text=True)
    assert os.path.exists(out), r.stderr
    print(y, len(feats), os.path.getsize(out) // 1024, "KB")

# page tables
owners = []
for o in names:
    e = OW[o]
    owners.append({"n": o, "c": e["cls"][0], "pc": plain_col(o)})
emb = {}
for k, v in EM.items():
    o, y = k.rsplit("|", 1)
    d = {"k": {"flag": "f", "arms": "a", "plain": "c", "people": "h", "group": "g"}[v["kind"]]}
    if v.get("file"):
        d["f"] = FM[v["file"]]["id"]
        if v.get("start") is not None: d["s"] = v["start"]
        if v.get("end") is not None: d["e"] = v["end"]
        d["b"] = v.get("basis", "")[:1]
    if v.get("q"):
        d["q"] = v["q"]
    emb.setdefault(y, {})[OID[o]] = d
flags = {m["id"]: {"fn": fn, "u": urllib.parse.quote(fn.replace(" ", "_")), "w": m["w"], "h": m["h"], "col": m["col"], "lic": m["lic"]} for fn, m in FM.items()}
qlab = {}
for v in EM.values():
    q = v.get("q")
    if q and q in IT:
        it = IT[q]; qlab[q] = [it["labs"][0], it["inc"], it["dis"]]
jsave({"years": YEARS, "owners": owners, "emb": emb, "flags": flags, "q": qlab}, f"{DATA}/site.json")

# reusable table: every area in every snapshot
with open(f"{DATA}/areas.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["year", "name", "owner_subjecto", "owner", "owner_class", "border_precision", "land_km2", "emblem", "emblem_file",
                "emblem_start", "emblem_end", "emblem_basis", "wikidata", "label_lon", "label_lat"])
    for y in YEARS:
        for f in SN[str(y)]:
            o = f["owner"]; e = EM.get(f"{o}|{y}", {}) if o else {}
            w.writerow(dash([y, f["NAME"] or "", f["SUBJECTO"] or "", o or "", OW[o]["cls"] if o else "unclaimed", f["BP"] or "", round(f["area"]),
                             e.get("kind", "none"), e.get("file") or "", e.get("start") if e.get("start") is not None else "",
                             e.get("end") if e.get("end") is not None else "", e.get("basis", ""), e.get("q", ""), f["pt"][0], f["pt"][1]]))
tot = sum(os.path.getsize(f"{MAPS}/{y}.json") for y in YEARS)
print("maps", round(tot / 1e6, 2), "MB; site.json", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")

# present-day reference layers for the page: city names and borders (Natural Earth, public domain)
pp = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
cities = sorted(({"name": p["properties"]["name"], "lat": round(p["properties"]["latitude"], 3), "lon": round(p["properties"]["longitude"], 3),
                  "pop": p["properties"]["pop_max"]} for p in pp if p["properties"]["pop_max"] >= 300000), key=lambda c: -c["pop"])[:900]
jsave(cities, f"{DATA}/cities.json")
ne = jload(NE50)
jsave({"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": f["geometry"], "properties": {}} for f in ne["features"]]}, f"{WORK}/ne50.json")
subprocess.run(["mapshaper", "-i", f"{WORK}/ne50.json", "-simplify", "percentage=12%", "keep-shapes", "-innerlines", "-o", f"{DATA}/borders_today.json",
                "format=topojson", "quantization=20000", "force"], capture_output=True, check=True)
print("cities", len(cities), "borders", os.path.getsize(f"{DATA}/borders_today.json") // 1024, "KB")
