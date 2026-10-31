"""Shared paths and helpers for the flags-through-time project.

Raw inputs (read in place, never copied into the repo):
  HB      /home/claude/newdata/raw2/historical-basemaps/  aourednik/historical-basemaps (GPL-3.0), Ourednik A. and
          contributors. geojson/world_<year>.geojson, properties NAME, ABBREVN, SUBJECTO (controlling entity), PARTOF,
          BORDERPRECISION (1 approximate, 2 moderately precise, 3 set by international law).
  WD      /home/claude/newdata/raw2/flags/hb_wikidata.tsv  QLever results: every basemap NAME matched to Wikidata items by
          English label (rdfs:label) or alias (skos:altLabel), with P41 flag (and start/end qualifiers), P94 coat of
          arms, P571 inception, P576 dissolution and sitelink count. Wikidata is CC0.
  FLAGS   /home/claude/newdata/raw2/flags/png/NNNN.png and flag_index.json: 160 px thumbnails of the Commons files,
          with each file's licence. Files are credited one by one in data/flag_credits.csv.
  GEO     /home/claude/newdata/raw/geo/ne_10m_admin_0_countries.geojson (Natural Earth, public domain).
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = "/home/claude/newdata/raw2/historical-basemaps"
WD = "/home/claude/newdata/raw2/flags/hb_wikidata.tsv"
FLAGS = "/home/claude/newdata/raw2/flags"
GEO = "/home/claude/newdata/raw/geo"
NE10 = f"{GEO}/ne_10m_admin_0_countries.geojson"
NE50 = f"{GEO}/ne_50m_admin_0_countries.geojson"
DATA = os.path.join(ROOT, "data")
MAPS = os.path.join(DATA, "maps")
FLAGDIR = os.path.join(DATA, "flags")
WORK = os.environ.get("FLAGSTMP", "/dev/shm/flags")   # intermediates live in memory, not in the repo
for d in (DATA, MAPS, FLAGDIR, WORK):
    os.makedirs(d, exist_ok=True)

# Snapshots used: every basemap year from 800 to 2010 (flags make little sense earlier).
YEARS = [800, 900, 1000, 1100, 1200, 1279, 1300, 1400, 1492, 1500, 1530, 1600, 1650, 1700, 1715, 1783, 1800, 1815,
         1878, 1880, 1900, 1914, 1920, 1930, 1938, 1945, 1960, 1994, 2000, 2010]

SLUG = "flags-through-time"
URL = "https://maps.tristanhotham.com/flags-through-time/"
REPO = "https://github.com/Tristan-Hotham/flags-through-time"
DOI = "10.5281/zenodo.23845995"
DOI_URL = "https://doi.org/10.5281/zenodo.23845995"
BLOG = "https://blog.tristanhotham.com/2026/10/31/flags-through-time/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
COMMONS = "https://commons.wikimedia.org/wiki/File:"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from names taken from Wikidata and the basemaps (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


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
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "yr": return str(int(v))
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "m1": return f"{float(v) / 1e6:.1f}"   # km2 to million km2
    raise ValueError(f)


def fill(text, R, f=fmt):
    return re.sub(r"\{\{(?!IMG|DOI|BLOG_URL|DOI_URL|TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: f(get(R, m.group(1)), m.group(3)), text)


def check_dashes(text, where):
    for bad in ("—", "–", "--"):
        assert bad not in text, (where, bad, text[max(0, text.find(bad) - 80):text.find(bad) + 80])
