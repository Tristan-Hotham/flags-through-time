"""Every number quoted anywhere (page, paper, blog, collage, post) is computed here and written to data/results.json.
Also data/entities.csv (one row per owner and snapshot), data/flag_age.csv and data/city_histories.csv."""
import csv, collections
from shapely.geometry import shape, Point
from common import *
from overrides import ITEMS, EXTRA, KNOWN_SINCE

SN = jload(f"{WORK}/snaps_owned.json")
OW = jload(f"{WORK}/owners.json")
EM = jload(f"{WORK}/emblems.json")
IT = jload(f"{WORK}/items.json")
FM = jload(f"{WORK}/flagmeta.json")
LAND = jload(f"{WORK}/land.json")
MR = jload(f"{WORK}/match_report.json")
R = {"years": YEARS, "n_snapshots": len(YEARS), "first_year": YEARS[0], "last_year": YEARS[-1]}

# ---------- land by emblem kind, per snapshot ----------
cover = []
for y in YEARS:
    tot = LAND[str(y)]["total"]
    k = collections.Counter()
    for f in SN[str(y)]:
        o = f["owner"]
        kind = EM[f"{o}|{y}"]["kind"] if o else "none"
        k[kind] += f["area"]
    cover.append({"y": y, **{kk: round(100 * k[kk] / tot, 1) for kk in ("flag", "arms", "plain", "people", "group", "none")}})
R["cover"] = cover
cy = {c["y"]: c for c in cover}
R["flag_share_1000"], R["flag_share_1500"], R["flag_share_1800"] = cy[1000]["flag"], cy[1500]["flag"], cy[1800]["flag"]
R["flag_share_1900"], R["flag_share_2010"] = cy[1900]["flag"], cy[2010]["flag"]
R["people_share_1000"], R["people_share_1492"] = cy[1000]["people"], cy[1492]["people"]
R["none_share_1000"] = cy[1000]["none"]
R["land_total_mkm2"] = round(LAND["2010"]["total"] / 1e6, 1)
R["first_flag_half"] = min(c["y"] for c in cover if c["flag"] + c["arms"] >= 50)
assert R["first_flag_half"] in YEARS

# ---------- distinct ruling entities and the largest ----------
by_year = {}
for y in YEARS:
    a = collections.Counter()
    for f in SN[str(y)]:
        if f["owner"]:
            a[f["owner"]] += f["area"]
    by_year[y] = a
ent = []
for y in YEARS:
    a = by_year[y]
    st = {o: v for o, v in a.items() if OW[o]["cls"] == "state" and v > 0}
    top = sorted(st.items(), key=lambda t: -t[1])[:3]
    ent.append({"y": y, "states": len(st), "all": sum(1 for v in a.values() if v > 0),
                "people": sum(1 for o, v in a.items() if OW[o]["cls"] == "people" and v > 0),
                "top": [{"n": o, "a": round(v), "pct": round(100 * v / LAND[str(y)]["total"], 1)} for o, v in top]})
R["entities"] = ent
ey = {e["y"]: e for e in ent}
R["states_min"] = min(ent, key=lambda e: e["states"]); R["states_max"] = max(ent, key=lambda e: e["states"])
R["states_2010"], R["states_1000"], R["states_1900"], R["states_1800"] = ey[2010]["states"], ey[1000]["states"], ey[1900]["states"], ey[1800]["states"]
big = max(((e["y"], e["top"][0]) for e in ent), key=lambda t: t[1]["a"])
R["largest_ever"] = {"y": big[0], **big[1]}
R["largest_by_year"] = [{"y": e["y"], **e["top"][0]} for e in ent]
# the British Empire at its peak: UK-owned land
uk = [(y, by_year[y].get("United Kingdom", 0)) for y in YEARS]
pk = max(uk, key=lambda t: t[1])
R["uk_peak"] = {"y": pk[0], "a": round(pk[1]), "pct": round(100 * pk[1] / LAND[str(pk[0])]["total"], 1)}
DOM = ("United Kingdom", "Canada", "Australia", "New Zealand", "Union of South Africa", "Newfoundland")
ukd = [(y, sum(by_year[y].get(k, 0) for k in DOM)) for y in YEARS if y <= 1945]
pk = max(ukd, key=lambda t: t[1])
R["uk_dom_peak"] = {"y": pk[0], "a": round(pk[1]), "pct": round(100 * pk[1] / LAND[str(pk[0])]["total"], 1)}
R["people_1492_americas"] = sum(1 for o, v in by_year[1492].items() if v > 0 and OW[o]["cls"] == "people" and
                                all(f["pt"][0] < -25 for f in SN["1492"] if f["owner"] == o))
assert R["people_1492_americas"] <= ey[1492]["people"]
R["land_by_year"] = {str(y): LAND[str(y)]["total"] for y in YEARS}
R["mongol_peak"] = max(({"y": y, "a": round(by_year[y]["Mongol Empire"]), "pct": round(100 * by_year[y]["Mongol Empire"] / LAND[str(y)]["total"], 1)}
                        for y in YEARS if by_year[y].get("Mongol Empire")), key=lambda d: d["a"])
R["qing_peak"] = max(({"y": y, "a": round(by_year[y]["Qing Empire"]), "pct": round(100 * by_year[y]["Qing Empire"] / LAND[str(y)]["total"], 1)}
                      for y in YEARS if by_year[y].get("Qing Empire")), key=lambda d: d["a"])
R["russia_peak"] = max(({"y": y, "a": round(by_year[y][k]), "n": k} for y in YEARS for k in ("Russian Empire", "Russia", "USSR") if by_year[y].get(k)), key=lambda d: d["a"])

# ---------- European empires, 1492 to 2010 ----------
EURO = {"United Kingdom", "England", "England and Ireland", "Scotland", "France", "Kingdom of France", "Spain", "Castile", "Aragón", "Portugal",
        "Netherlands", "Belgium", "Germany", "German Empire", "Prussia", "Italy", "Kingdom of Italy", "Denmark", "Denmark-Norway", "Sweden",
        "Sweden-Norway", "Norway", "Austrian Empire", "Austria-Hungary", "Holy Roman Empire", "Venice", "Genoa", "Kalmar Union",
        "Poland-Lithuania", "Russian Empire", "Russia", "Tsardom of Muscovy", "Grand Duchy of Moscow", "USSR", "Dutch East Indies",
        "Viceroyalty of New Spain", "Viceroyalty of the Río de la Plata", "British East India Company", "Viceroyalty of Peru", "Habsburg Austria"}
RUS = {"Russian Empire", "Russia", "Tsardom of Muscovy", "Grand Duchy of Moscow", "USSR"}


def in_europe(x, y):
    return -25 <= x <= 60 and 35 <= y <= 72 and not (y < 42 and x > 26)


eu = []
for y in [v for v in YEARS if v >= 1492]:
    k = collections.Counter()
    for f in SN[str(y)]:
        o = f["owner"]
        if o not in EURO:
            continue
        x, yy = f["pt"]
        part = "russia" if o in RUS else ("home" if in_europe(x, yy) else "overseas")
        k[part] += f["area"]
    tot = LAND[str(y)]["total"]
    eu.append({"y": y, **{p: round(100 * k[p] / tot, 1) for p in ("home", "russia", "overseas")}, "all": round(100 * sum(k.values()) / tot, 1)})
R["euro"] = eu
ep = max(eu, key=lambda d: d["all"]); R["euro_peak"] = ep
R["euro_overseas_peak"] = max(eu, key=lambda d: d["overseas"])
R["euro_1492"], R["euro_2010"] = eu[0], eu[-1]
# colonies the basemap labels as their own owner in 1920 and 1930 but under a European power in both 1914 and 1938
own14 = {f["NAME"]: f["owner"] for f in SN["1914"] if f["NAME"]}
own38 = {f["NAME"]: f["owner"] for f in SN["1938"] if f["NAME"]}
gap = {}
for y in (1920, 1930):
    g = sum(f["area"] for f in SN[str(y)] if f["NAME"] and f["owner"] not in EURO and own14.get(f["NAME"]) in EURO and own38.get(f["NAME"]) in EURO)
    gap[y] = round(100 * g / LAND[str(y)]["total"], 1)
R["euro_label_gap"] = gap
R["euro_peak_ex_russia"] = max(({"y": d["y"], "v": round(d["home"] + d["overseas"], 1)} for d in eu), key=lambda d: d["v"])

# ---------- the flag-age chart: present-day countries ----------
ne = jload(NE10)["features"]
countries = []
for f in ne:
    p = f["properties"]
    if p["TYPE"] == "Sovereign country" or (p["TYPE"] == "Country" and p["ADMIN"] == p["SOVEREIGNT"]):
        countries.append((p["ADMIN"], p["WIKIDATAID"], p["ISO_A3"] if p["ISO_A3"] != "-99" else p["ADM0_A3"]))
rows, ages = [], []
for name, q, iso in sorted(countries):
    it = IT.get(q)
    if it and it.get("extra"):
        it = None                     # flags filled from flag-icons carry no Wikidata date: left out of this chart
    cur = [fl for fl in (it["flags"] if it else []) if fl[2] is None and fl[1] is not None and "civil" not in fl[0].lower() and "naval" not in fl[0].lower()]
    best = max(cur, key=lambda fl: fl[1]) if cur else None
    rows.append({"country": name, "iso_a3": iso, "wikidata": q, "in_data": bool(it), "current_flag": best[0] if best else "",
                 "adopted": best[1] if best else ""})
    if best:
        ages.append(best[1])
with open(f"{DATA}/flag_age.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(dash(rows))
bins = collections.Counter((a // 20) * 20 for a in ages)
R["flag_age"] = {"n_countries": len(countries), "n_in_data": sum(1 for r in rows if r["in_data"]), "n_dated": len(ages),
                 "coverage_pct": round(100 * len(ages) / len(countries)), "bins": [{"b": b, "n": bins[b]} for b in sorted(bins)],
                 "median": sorted(ages)[len(ages) // 2], "oldest": sorted([r for r in rows if r["adopted"] != ""], key=lambda r: r["adopted"])[:5],
                 "since_1945": sum(1 for a in ages if a >= 1945), "since_1990": sum(1 for a in ages if a >= 1990)}
R["flag_age"]["since_1945_pct"] = round(100 * R["flag_age"]["since_1945"] / len(ages))
R["flag_age"]["since_1990_pct"] = round(100 * R["flag_age"]["since_1990"] / len(ages))
R["flag_age"]["top_bin"] = dict(max(R["flag_age"]["bins"], key=lambda d: d["n"]))
R["flag_age"]["top_bin"]["e"] = R["flag_age"]["top_bin"]["b"] + 19

# ---------- what flew over a city ----------
CITIES = [("Boston", -71.06, 42.36), ("Beijing", 116.40, 39.90), ("Venice", 12.33, 45.44), ("Delhi", 77.21, 28.61), ("Istanbul", 28.98, 41.01),
          ("Vienna", 16.37, 48.21), ("Moscow", 37.62, 55.75), ("Mexico City", -99.13, 19.43), ("Cairo", 31.24, 30.04), ("London", -0.13, 51.51),
          ("Jerusalem", 35.21, 31.77), ("Sydney", 151.21, -33.87), ("Lagos", 3.39, 6.45), ("Lima", -77.04, -12.05), ("Algiers", 3.06, 36.75), ("Hanoi", 105.85, 21.03)]
hist, chist = {}, []
for y in YEARS:
    raw = jload(f"{HB}/geojson/world_{y}.geojson")["features"]
    feats = [(f, shape(raw[f["i"]]["geometry"]).buffer(0)) for f in SN[str(y)]]
    for c, x, yy in CITIES:
        pt = Point(x, yy)
        hit = sorted([f for f, g in feats if g.contains(pt)], key=lambda f: f["area"])
        if not hit:   # a coastal city just outside the simplified coastline: take the nearest area within 0.3 degrees
            near = sorted(((g.distance(pt), f) for f, g in feats if g.distance(pt) < .3), key=lambda t: t[0])
            hit = [near[0][1]] if near else []
        f = hit[0] if hit else None
        o = f["owner"] if f else None
        e = EM.get(f"{o}|{y}", {"kind": "none"}) if o else {"kind": "none"}
        hist.setdefault(c, []).append({"y": y, "n": f["NAME"] if f else None, "o": o, "k": e["kind"], "f": FM[e["file"]]["id"] if e.get("file") else None})
        chist.append([c, y, f["NAME"] if f else "", o or "", e["kind"], e.get("file", "")])
R["cities"] = [{"c": c, "x": x, "y": yy, "h": hist[c], "n_owners": len({h["o"] for h in hist[c] if h["o"]}),
                "n_flags": len({h["f"] for h in hist[c] if h["f"]})} for c, x, yy in CITIES]
with open(f"{DATA}/city_histories.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["city", "year", "area_name", "owner", "emblem", "emblem_file"]); w.writerows(dash(chist))
cb = {c["c"]: c for c in R["cities"]}
R["boston_seq"] = [h["o"] for h in cb["Boston"]["h"]]
R["most_owners_city"] = max(R["cities"], key=lambda c: c["n_owners"])

# ---------- matching and emblem statistics ----------
st = {o: e for o, e in OW.items() if e["cls"] == "state"}
R["match"] = {"n_owners": len(OW), "n_state": len(st), "n_people": MR["n_people"], "n_group": MR["n_group"], "n_state_matched": MR["n_state_matched"],
              "rate": MR["match_rate_states"], "rate_area": MR["match_rate_area"], "n_overrides": len(ITEMS), "n_extra": len(EXTRA), "n_known": len(KNOWN_SINCE)}
kinds = collections.Counter(); basis = collections.Counter()
for k, e in EM.items():
    if OW[k.rsplit("|", 1)[0]]["cls"] == "state":
        kinds[e["kind"]] += 1
        if e["kind"] == "flag":
            basis[e["basis"]] += 1
R["emblems"] = {"state_years": sum(kinds.values()), **{k: kinds[k] for k in ("flag", "arms", "plain")}, "basis": dict(basis)}
R["emblems"]["flag_pct"] = round(100 * kinds["flag"] / sum(kinds.values()))
R["emblems"]["undated_pct_of_flags"] = round(100 * basis["undated"] / kinds["flag"])
lic = collections.Counter(m["lic"] for m in FM.values())
R["images"] = {"n": len(FM), "flags": sum(1 for m in FM.values() if m["kind"] == "flag"), "arms": sum(1 for m in FM.values() if m["kind"] == "arms"),
               "pd": sum(v for k, v in lic.items() if k.startswith("Public domain") or k == "CC0"),
               "by_sa": sum(v for k, v in lic.items() if "BY-SA" in k), "other": sum(v for k, v in lic.items() if not (k.startswith("Public domain") or k == "CC0" or "BY-SA" in k))}
R["n_flags_used_2010"] = len({EM[f"{f['owner']}|2010"].get("file") for f in SN["2010"] if f["owner"] and EM[f"{f['owner']}|2010"].get("file")})
R["owners_with_flag"] = len({k.rsplit("|", 1)[0] for k, e in EM.items() if e["kind"] == "flag"})
R["fixes"] = 2

# entities.csv
with open(f"{DATA}/entities.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["owner", "class", "year", "land_km2", "share_of_land_pct", "emblem", "emblem_file", "emblem_start", "emblem_end", "emblem_basis",
                "wikidata", "wikidata_label", "match_method", "subjecto_spellings"])
    for o in sorted(OW, key=lambda o: -sum(OW[o]["years"].values())):
        e = OW[o]
        for y in sorted(e["years"], key=int):
            m = EM[f"{o}|{y}"]; q = m.get("q", "")
            w.writerow(dash([o, e["cls"], y, round(e["years"][y]), round(100 * e["years"][y] / LAND[str(y)]["total"], 3), m["kind"], m.get("file", ""),
                             m.get("start") if m.get("start") is not None else "", m.get("end") if m.get("end") is not None else "", m.get("basis", ""),
                             q, IT[q]["labs"][0] if q in IT else "", e["how"] or "", "; ".join(sorted(e["raw"]))]))
R["retrieved"] = "2026"
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("flag_share_1000", "flag_share_1500", "flag_share_1800", "flag_share_1900", "flag_share_2010", "first_flag_half",
                                    "largest_ever", "uk_peak", "mongol_peak", "qing_peak", "russia_peak", "euro_peak", "euro_overseas_peak",
                                    "euro_peak_ex_russia", "states_min", "states_max", "match", "emblems", "images")}, ensure_ascii=False, indent=0)[:3500])
print(R["flag_age"]["n_countries"], R["flag_age"]["n_dated"], R["flag_age"]["bins"], R["flag_age"]["median"], R["flag_age"]["oldest"][:3])
for e in ent: print(e["y"], e["states"], e["people"], [(t["n"], t["pct"]) for t in e["top"]])
for d in eu: print(d)
print(R["boston_seq"])
