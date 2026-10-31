"""Match every controlling entity (SUBJECTO) in the snapshots to Wikidata, and choose the emblem shown for it in each
snapshot year: a flag in use that year, a coat of arms or royal banner, a plain colour, or the neutral style for peoples
and cultural regions. No flag is ever invented: an area gets a flag only if Wikidata records one for that entity and the
rules below find it plausible for that year.

Rules for a flag in year y (statements from the entity's Wikidata items, fictitious and conjectural files left out):
 1. dated: a flag whose start and end (P41 qualifiers, else years in the Commons file name) cover y. Latest start wins.
 2. undated: a flag with no date at all, for an entity that no longer exists, if y lies within its inception and
    dissolution and y >= 1150; for a present-day entity, only from 1900 on.
 3. arms: the coat of arms (P94) of a historical entity within its lifespan from 1150 (heraldry began in the 12th
    century), or any coat of arms whose file name dates cover y.
 4. plain: otherwise a plain colour with the name.
Peoples, cultural regions and loose groups of states never get a flag, whatever Wikidata holds for them.
Output: WORK/owners.json, WORK/emblems.json, WORK/match_report.json."""
import math, collections, urllib.parse
from common import *
from overrides import *

# ---------- Wikidata rows ----------
txt = open(WD, encoding="utf-8").read()
rows = []
for sec in txt.split("#####\n"):
    lines = sec.strip("\n").split("\n")
    how, head = lines[0].strip(), [h.lstrip("?") for h in lines[1].split("\t")]
    for ln in lines[2:]:
        f = ln.split("\t"); f += [""] * (len(head) - len(f))
        r = {"how": how}
        for h, v in zip(head, f):
            v = v.strip()
            if v.startswith("<http://www.wikidata.org/entity/"):
                v = v[32:-1]
            elif v.startswith("<") and v.endswith(">"):
                v = v[1:-1]
            else:
                m = re.match(r'^"(.*)"(@[\w-]+|\^\^<[^>]+>)?$', v, re.S)
                if m:
                    v = m.group(1)
            r[h] = v
        rows.append(r)

FI = jload(f"{FLAGS}/flag_index.json")


def fname(url):
    return urllib.parse.unquote(url.rsplit("/", 1)[-1]) if url else None


def year(s):
    m = re.match(r"^(-?)(\d{1,4})-", s or "")
    return (-1 if m.group(1) else 1) * int(m.group(2)) if m else None


ROMAN = {"X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18}


def name_dates(fn):
    """Years written in a Commons file name: '(1889–1912)', '1701-1935', '(1495)', 'vor 1433', 'XII-XIII', '14Jh', '15th Century'."""
    s = fn.rsplit(".", 1)[0]
    m = re.search(r"(1[0-9]{3}|[5-9][0-9]{2})\s*[–\-]\s*(1[0-9]{3}|20[0-9]{2})", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"vor (1[0-9]{3})", s)
    if m:
        return None, int(m.group(1))
    m = re.search(r"\b(X{1,2}V?I{0,3}|XI{1,3}V?)\s*-\s*(X{1,2}V?I{0,3})\b", s)
    if m and m.group(1) in ROMAN and m.group(2) in ROMAN:
        return (ROMAN[m.group(1)] - 1) * 100, ROMAN[m.group(2)] * 100 - 1
    m = re.search(r"\b(1[0-9])(?:Jh|th [Cc]entury)", s)
    if m:
        c = int(m.group(1)); return (c - 1) * 100, c * 100 - 1
    m = re.search(r"\((1[0-9]{3})\)", s)
    if m:
        return int(m.group(1)), None
    return None, None


ITEM = {}
LAB = collections.defaultdict(list)
for r in rows:
    q = r["item"]
    it = ITEM.setdefault(q, {"q": q, "labs": set(), "sl": int(r["sl"] or 0), "inc": year(r["inc"]), "dis": year(r["dis"]), "flags": [], "coa": set()})
    it["labs"].add(r["lab"])
    if it["inc"] is None: it["inc"] = year(r["inc"])
    if it["dis"] is None: it["dis"] = year(r["dis"])
    fn = fname(r["flag"])
    if fn:
        st = (fn, year(r["fstart"]), year(r["fend"]))
        if st not in it["flags"]:
            it["flags"].append(st)
    if r["coa"]:
        it["coa"].add(fname(r["coa"]))
    if (q, r["how"]) not in LAB[r["lab"]]:
        LAB[r["lab"]].append((q, r["how"]))
for q, x in EXTRA.items():   # present-day flags filled from flag-icons (see overrides.py and 03_flags.py)
    ITEM[q] = {"q": q, "labs": {x["lab"]}, "sl": 0, "inc": x["inc"], "dis": None, "flags": [(x["file"], x["start"], None)], "coa": set(), "extra": x["code"]}
    FI[x["file"]] = {"png": f"extra_{x['code']}.png", "lic": "Public domain", "extra": x["code"]}
# files that are a present-day country's flag (an open-ended statement of an entity that still exists), with its start
MODERN_FILES = {}
for it in ITEM.values():
    if it["dis"] is None and it["inc"] is not None:
        for fn, fs, fe in it["flags"]:
            if fe is None and name_dates(fn) == (None, None):
                MODERN_FILES[fn] = min(MODERN_FILES.get(fn, 9999), fs if fs is not None else 9999)
for fn, (y0, _) in KNOWN_SINCE.items():
    MODERN_FILES[fn] = y0
BAD = re.compile(r"fictitious|conjectural|fictional|proposed|hypothetical|unofficial", re.I)

# ---------- owners in the snapshots ----------
FIXES = {  # basemap labelling errors corrected here (documented on the page and in the paper)
    (1930, "White Russia", "White Russia"): ("USSR", "USSR", "the 1930 polygon of the Soviet Union is labelled White Russia in the basemap; it is the same polygon as the 1920 USSR"),
    (1930, "Far Eastern SSR", "Far Eastern SSR"): ("Far Eastern SSR", "USSR", "the Far Eastern Republic joined Soviet Russia in 1922; in 1930 its land was Soviet"),
}


def owner_of(f, y):
    n, s = f["NAME"], f["SUBJECTO"]
    if (y, n, s) in FIXES and (y != 1930 or n != "White Russia" or f["area"] > 1e7):
        n, s, _ = FIXES[(y, n, s)]
        f["NAME"], f["SUBJECTO"], f["fixed"] = n, s, True
    raw = s or n
    if raw is None or raw == "Antarctica":
        return None, None
    tag = None
    for v in (n, s):
        m = re.search(r"\(([^)]*)\)\s*$", v or "")
        if m and m.group(1) in POWER_TAG and (s is None or s == n):
            tag = POWER_TAG[m.group(1)]
    own = tag or CANON.get(raw, raw)
    return own, raw


def low(s):
    return s.lower()


def classify(o, it):
    lo = low(o)
    words = set(re.findall(r"[a-z\-]+", lo))
    if o in NOT_PEOPLE or o in ITEMS:
        return "state"
    if o in PEOPLE or any(w in words for w in ("hunter", "hunters", "gatherers", "hunter-gatherers", "peoples", "tribes", "farmers", "nomads",
                                               "nomadic", "cultures", "foragers", "fishers", "fichers", "herders", "pastoralists", "foraging")):
        return "people"
    if any(w in words for w in ("states", "kingdoms", "khanates", "emirates", "principalities", "sultanates", "city-states", "chiefdoms",
                                "warlords", "confederacies", "clans", "princedoms", "settlements", "territories", "cities")):
        return "group"
    if any(w in words for w in STATE_WORDS):
        return "state"
    if o in MODERN:
        return "state"
    pts = PTS.get(o, [])
    if pts and max(OWN[o]["years"]) <= 1880 and all(x < -25 or (110 < x < 155 and y < -10) for x, y in pts):
        return "people"     # indigenous nations of the Americas and Australia, as the basemap names them
    return "state"


snaps = {y: jload(f"{WORK}/snap_{y}.json")["features"] for y in YEARS}
MODERN = {f["SUBJECTO"] or f["NAME"] for f in snaps[2010] if f["NAME"]} | {f["NAME"] for f in snaps[2010] if f["NAME"]}
OWN, PTS = {}, {}
for y in YEARS:
    for f in snaps[y]:
        o, raw = owner_of(f, y)
        f["owner"] = o
        if o is None:
            continue
        e = OWN.setdefault(o, {"name": o, "raw": collections.Counter(), "years": {}, "names": collections.Counter()})
        e["raw"][raw] += 1
        e["years"][y] = e["years"].get(y, 0) + f["area"]
        e["names"][f["NAME"]] += 1
        PTS.setdefault(o, []).append(f["pt"])
jsave({y: snaps[y] for y in YEARS}, f"{WORK}/snaps_owned.json")


# ---------- choose a Wikidata item for each owner ----------
def score(q, how, yrs):
    it = ITEM[q]; s = math.log10(it["sl"] + 1) + (0.5 if how == "rdfs:label" else 0) + (0.6 if it["flags"] or it["coa"] else 0)
    lo, hi = min(yrs), max(yrs)
    if it["inc"] is not None:
        if it["inc"] > hi + 60:
            return -99                       # founded long after the area appears: a namesake (a town, a ship, a modern body)
        end = it["dis"] if it["dis"] is not None else 2100
        cov = sum(1 for y in yrs if it["inc"] - 60 <= y <= end + 60) / len(yrs)
        if it["dis"] is not None and it["dis"] < lo - 60:
            return -99                       # dissolved long before
        s += 3 * cov
    return s


def pick(o, yrs):
    best = None
    for lab in dict.fromkeys([o] + [k for k, _ in OWN[o]["raw"].most_common()]):
        for q, how in LAB.get(lab, []):
            sc = score(q, how, yrs)
            if best is None or sc > best[0]:
                best = (sc, q, how, lab)
    if best and best[0] > 1.0:
        return best
    return None


def pick_year(o, y):
    """The best Wikidata item for owner o in year y: one whose lifespan covers y, else one with no dates at all."""
    best = None
    for lab in dict.fromkeys([o] + [k for k, _ in OWN[o]["raw"].most_common()]):
        for q, how in LAB.get(lab, []):
            it = ITEM[q]
            s = math.log10(it["sl"] + 1) + (0.5 if how == "rdfs:label" else 0) + (0.6 if it["flags"] or it["coa"] else 0)
            if it["inc"] is not None:
                if not (it["inc"] - 30 <= y and (it["dis"] is None or y <= it["dis"] + 30)):
                    continue
                s += 2
            if best is None or s > best[0]:
                best = (s, q, how)
    return best if best and best[0] > 1.0 else None


def emblem(o, y, items, cls):
    if cls != "state":
        return {"kind": cls}
    cands = []
    for rank, q in enumerate(items):
        it = ITEM.get(q)
        if not it:
            continue
        for fn, fs, fe in it["flags"]:
            if BAD.search(fn) or fn not in FI:
                continue
            ns, ne = name_dates(fn)
            s, e = (fs if fs is not None else ns), (fe if fe is not None else ne)
            if s is not None or e is not None:
                lo = s if s is not None else -9999
                hi = e if e is not None else (it["dis"] if it["dis"] is not None else 9999)
                if s is None and e is not None:
                    lo = max(it["inc"] if it["inc"] is not None else -9999, 1150)
                if lo <= y <= hi:
                    cands.append((1, -(lo if lo > -9999 else 0), hi - lo, rank, {"kind": "flag", "file": fn, "start": s, "end": e, "q": q,
                                                                               "basis": "dated" if fs is not None or fe is not None else "file"}))
            else:
                if fn in MODERN_FILES:     # a present-day flag: shown only from its known start, else from 1900
                    st0 = MODERN_FILES[fn] if MODERN_FILES[fn] < 9999 else 1900
                    ok = y >= st0 and (it["inc"] is None or it["inc"] <= y) and (it["dis"] is None or y <= it["dis"])
                    if ok and fn in KNOWN_SINCE and y < 1900:
                        cands.append((2, 0, 0, rank, {"kind": "flag", "file": fn, "start": None, "end": None, "q": q, "basis": "known"}))
                        continue
                elif it["dis"] is not None:
                    ok = y >= 1150 and (it["inc"] is None or it["inc"] <= y) and y <= it["dis"]
                else:
                    ok = y >= 1900 and it["inc"] is not None and it["inc"] <= y
                if ok:
                    cands.append((2, 0 if norm(o) in norm(fn) else 1, 0, rank, {"kind": "flag", "file": fn, "start": None, "end": None, "q": q, "basis": "undated"}))
        for fn in sorted(it["coa"]):
            if BAD.search(fn) or fn not in FI:
                continue
            ns, ne = name_dates(fn)
            if ns is not None or ne is not None:
                ok = (ns or -9999) <= y <= (ne or (it["dis"] or 9999))
            else:   # undated arms: only for a historical entity of under 400 years (long-lived states changed their arms)
                ok = (it["dis"] is not None and it["inc"] is not None and it["dis"] - it["inc"] < 400 and y >= 1150
                      and it["inc"] <= y <= it["dis"])
            if ok:
                cands.append((3, 0, 0, rank, {"kind": "arms", "file": fn, "start": ns, "end": ne, "q": q, "basis": "arms"}))
    if not cands:
        return {"kind": "plain", "q": items[0] if items else None}
    cands.sort(key=lambda c: c[:4])
    return cands[0][4]


owners, EMB, report = {}, {}, collections.Counter()
for o, e in OWN.items():
    yrs = sorted(e["years"])
    m = None
    if o in ITEMS:
        items_by_year = {}
        for y in yrs:
            qs = [q for a, b, ql in ITEMS[o] if a <= y <= b for q in ql]
            items_by_year[y] = qs
        allq = [q for _, _, ql in ITEMS[o] for q in ql if q in ITEM]
        how = "override"
        for y in yrs:
            covered = any(a <= y <= b for a, b, _ in ITEMS[o])
            items_by_year[y] = [q for q in items_by_year[y] if q in ITEM]
            if not items_by_year[y] and not covered:
                p = pick_year(o, y)
                items_by_year[y] = [p[1]] if p else []
    else:
        picks = {y: pick_year(o, y) for y in yrs}
        items_by_year = {y: [p[1]] if p else [] for y, p in picks.items()}
        allq = [q for q, _ in collections.Counter(p[1] for p in picks.values() if p).most_common()]
        how = collections.Counter(p[2] for p in picks.values() if p).most_common(1)[0][0] if allq else None
    q0 = allq[0] if allq else None
    it = ITEM.get(q0)
    cls = classify(o, it)
    owners[o] = {"name": o, "cls": cls, "q": q0, "how": how, "sl": it["sl"] if it else None, "inc": it["inc"] if it else None,
                 "dis": it["dis"] if it else None, "raw": dict(e["raw"]), "years": e["years"], "items": sorted(set(allq))}
    for y in yrs:
        EMB[f"{o}|{y}"] = emblem(o, y, items_by_year[y], cls)
        if cls == "state" and items_by_year[y]:
            EMB[f"{o}|{y}"].setdefault("q", items_by_year[y][0])

# ---------- report ----------
area = lambda o: sum(OWN[o]["years"].values())
st = [o for o in owners if owners[o]["cls"] == "state"]
rep = {"n_owners": len(owners), "n_state": len(st), "n_people": sum(1 for o in owners if owners[o]["cls"] == "people"),
       "n_group": sum(1 for o in owners if owners[o]["cls"] == "group"),
       "n_state_matched": sum(1 for o in st if owners[o]["q"]), "n_override": sum(1 for o in owners if owners[o]["how"] == "override"),
       "area_state": sum(area(o) for o in st), "area_state_matched": sum(area(o) for o in st if owners[o]["q"])}
kinds = collections.Counter(); kinds_area = collections.Counter()
for k, v in EMB.items():
    o, y = k.rsplit("|", 1)
    kinds[v["kind"] + ("/" + v.get("basis", "") if v["kind"] == "flag" else "")] += 1
    kinds_area[v["kind"]] += OWN[o]["years"][int(y)]
rep["emblem_kinds"] = dict(kinds); rep["emblem_area"] = {k: round(v) for k, v in kinds_area.items()}
rep["match_rate_states"] = round(100 * rep["n_state_matched"] / rep["n_state"], 1)
rep["match_rate_area"] = round(100 * rep["area_state_matched"] / rep["area_state"], 1)
print(json.dumps(rep, indent=1))
jsave(owners, f"{WORK}/owners.json"); jsave(EMB, f"{WORK}/emblems.json"); jsave(rep, f"{WORK}/match_report.json", indent=1)
jsave({q: {**it, "labs": sorted(it["labs"]), "coa": sorted(it["coa"])} for q, it in ITEM.items()}, f"{WORK}/items.json")
