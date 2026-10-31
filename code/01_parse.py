"""Read the basemap snapshots, tidy the properties, and measure each feature's land area on an equal-area grid.

Overlapping polygons exist in the basemaps. To count land once, each snapshot is rasterised on a 0.1 degree grid,
largest features first, so smaller features (enclaves, city states) win where they overlap. Cell areas are weighted
by the cosine of latitude. Antarctica (south of 60S) is left out of every land total.
Output: WORK/snap_<year>.json (features with properties and area) and WORK/land.json (totals)."""
import numpy as np
from shapely.geometry import shape, mapping
from shapely.validation import make_valid
from rasterio import features as rfeat
from rasterio.transform import from_origin
from common import *

RES = 0.1
W, H = int(360 / RES), int(150 / RES)          # 90N to 60S
TR = from_origin(-180, 90, RES, RES)
lat = 90 - (np.arange(H) + .5) * RES
CELL = (RES * 111.32) ** 2 * np.cos(np.radians(lat))[:, None]   # km2 per cell


def clean(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


land = {}
for y in YEARS:
    gj = jload(f"{HB}/geojson/world_{y}.geojson")
    feats = []
    for i, f in enumerate(gj["features"]):
        p = f["properties"]
        if not f.get("geometry"):
            continue
        g = shape(f["geometry"])
        if not g.is_valid:
            g = make_valid(g)
        if g.is_empty:
            continue
        feats.append({"i": i, "NAME": clean(p.get("NAME")), "SUBJECTO": clean(p.get("SUBJECTO")), "PARTOF": clean(p.get("PARTOF")),
                      "ABBREVN": clean(p.get("ABBREVN")), "BP": p.get("BORDERPRECISION"), "g": g})
    order = sorted(range(len(feats)), key=lambda k: -feats[k]["g"].area)
    shapes = [(mapping(feats[k]["g"]), k + 1) for k in order]
    ras = rfeat.rasterize(shapes, out_shape=(H, W), transform=TR, fill=0, dtype="int32", all_touched=False)
    area = np.bincount(ras.ravel(), weights=np.broadcast_to(CELL, ras.shape).ravel(), minlength=len(feats) + 1)
    for k, f in enumerate(feats):
        f["area"] = round(float(area[k + 1]), 1)
        c = f["g"].representative_point()
        f["pt"] = [round(c.x, 3), round(c.y, 3)]
        del f["g"]
    tot = float(area[1:].sum())
    named = float(sum(f["area"] for f in feats if f["NAME"]))
    land[y] = {"total": round(tot), "named": round(named), "n_features": len(feats)}
    jsave({"year": y, "features": feats}, f"{WORK}/snap_{y}.json")
    print(y, len(feats), f"land {tot / 1e6:.1f}M km2, named {named / tot:.0%}")
jsave(land, f"{WORK}/land.json", indent=1)
