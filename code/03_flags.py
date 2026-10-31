"""Copy the flag and arms images actually used into data/flags/, compute each one's dominant colour, and write the
credits file data/flag_credits.csv (file, Commons page, licence, entities that use it).
Two present-day flags missing from the downloaded Commons set (see EXTRA in overrides.py) are rendered here from the
flag-icons SVGs (MIT licence), downloaded once from raw.githubusercontent.com into WORK/extra/."""
import csv, collections, subprocess, urllib.request, urllib.parse
from PIL import Image
from common import *
from overrides import EXTRA

E = jload(f"{WORK}/emblems.json")
FI = jload(f"{FLAGS}/flag_index.json")
EX = os.path.join(WORK, "extra"); os.makedirs(EX, exist_ok=True)
for q, x in EXTRA.items():
    svg, png = f"{EX}/{x['code']}.svg", f"{EX}/extra_{x['code']}.png"
    if not os.path.exists(svg):
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/{x['code']}.svg", svg)
    if not os.path.exists(png):
        js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:160,height:120}});"
              f"await p.goto('file://{svg}');await p.screenshot({{path:'{png}'}});await b.close();}})();")
        subprocess.run(["node", "-e", js], check=True, cwd="/tmp")
    FI[x["file"]] = {"png": None, "src": png, "lic": "Public domain (design); image from flag-icons, MIT", "extra": x["code"]}

users = collections.defaultdict(set)
kinds = {}
for k, e in E.items():
    if e.get("file"):
        users[e["file"]].add(k.rsplit("|", 1)[0])
        kinds[e["file"]] = e["kind"]


def dominant(im):
    im = im.convert("RGBA")
    px = [p for p in im.getdata() if p[3] > 128]
    c = collections.Counter(((r // 24) * 24 + 12, (g // 24) * 24 + 12, (b // 24) * 24 + 12) for r, g, b, a in px)
    tot = sum(c.values())
    for col, n in c.most_common():
        if not (min(col) > 200 or max(col) < 40) and n / tot > .03:   # skip white and black unless nothing else is there
            return "#%02x%02x%02x" % col
    return "#%02x%02x%02x" % c.most_common(1)[0][0]


for fn in os.listdir(FLAGDIR):
    os.remove(os.path.join(FLAGDIR, fn))
meta, rows = {}, []
for i, fn in enumerate(sorted(users)):
    src = FI[fn].get("src") or f"{FLAGS}/png/{FI[fn]['png']}"
    im = Image.open(src).convert("RGBA")
    if im.width > 160:
        im = im.resize((160, round(im.height * 160 / im.width)), Image.LANCZOS)
    fid = f"f{i:03d}"
    im.save(f"{FLAGDIR}/{fid}.png", optimize=True)
    meta[fn] = {"id": fid, "w": im.width, "h": im.height, "col": dominant(im), "lic": FI[fn]["lic"], "kind": kinds[fn]}
    extra = FI[fn].get("extra")
    rows.append({"file": fn, "image": f"flags/{fid}.png", "kind": kinds[fn],
                 "source": (f"https://github.com/lipis/flag-icons/blob/main/flags/4x3/{extra}.svg" if extra else COMMONS + urllib.parse.quote(fn.replace(" ", "_"))),
                 "licence": FI[fn]["lic"], "used_for": "; ".join(sorted(users[fn]))})
with open(f"{DATA}/flag_credits.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(dash(rows))
jsave(meta, f"{WORK}/flagmeta.json")
size = sum(os.path.getsize(f"{FLAGDIR}/{x}") for x in os.listdir(FLAGDIR))
print(len(meta), "images,", round(size / 1e6, 2), "MB;", collections.Counter(m["lic"] for m in meta.values()).most_common())
