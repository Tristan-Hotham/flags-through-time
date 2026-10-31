"""House style for static figures: fonts (a static Fraunces Black cut from the variable font, written to memory), colours,
and the world-in-flags map drawer (Equal Earth projection, flags clipped to each area's outline)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
import matplotlib.image as mpimg
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape, box
from common import *

FONTS = "/home/claude/ref/fonts"
FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": 900, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Black.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#646875", "axes.labelcolor": "#1E2430",
                     "xtick.color": "#646875", "ytick.color": "#646875", "hatch.linewidth": .6})
BG, FG, MUT, LAND, RULE, HOT, COOL, GOLD = "#F7F3EA", "#1E2430", "#646875", "#E9E2D2", "#E2DACA", "#B3261E", "#23408E", "#C99A06"
KC = {"flag": ("Flag in use", "#B3261E"), "arms": ("Coat of arms or royal banner", "#C99A06"), "plain": ("State, no flag recorded", "#8E9AAE"),
      "group": ("Group of small states", "#BFAF92"), "people": ("People or cultural region", "#A8936A"), "none": ("No holder named", "#DCD3C0")}
tr = Transformer.from_crs(4326, 8857, always_xy=True)
SITE = jload(f"{DATA}/site.json")
SN = jload(f"{WORK}/snaps_owned.json")
EM = jload(f"{WORK}/emblems.json")
FM = jload(f"{WORK}/flagmeta.json")
_IM = {}


def flagimg(fid):
    if fid not in _IM:
        _IM[fid] = mpimg.imread(f"{FLAGDIR}/{fid}.png")
    return _IM[fid]


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


PC = {o["n"]: o["pc"] for o in SITE["owners"]}
_GEO = {}


def parts(year, tol=.06, clip=(-180, -58, 180, 84)):
    """Simplified, projected polygon parts of every area in a snapshot: [(feature, [rings as arrays])...]."""
    if (year, tol) in _GEO:
        return _GEO[(year, tol)]
    raw = jload(f"{HB}/geojson/world_{year}.geojson")["features"]
    out = []
    for f in SN[str(year)]:
        g = shape(raw[f["i"]]["geometry"]).buffer(0).intersection(box(*clip)).simplify(tol, preserve_topology=True)
        if g.is_empty:
            continue
        polys = [g] if g.geom_type == "Polygon" else [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]
        for p in polys:
            rings = []
            for r in [p.exterior] + list(p.interiors):
                a = np.array(r.coords)
                x, y = tr.transform(a[:, 0], a[:, 1])
                rings.append(np.column_stack([x, y]))
            out.append((f, rings))
    _GEO[(year, tol)] = out
    return out


def ppath(rings):
    verts, codes = [], []
    for r in rings:
        verts += list(r); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 2) + [MPath.CLOSEPOLY]
    return MPath(verts, codes)


def world_flags(ax, year, ext=None, lw=.25, ec="#FFFFFF", tol=.06, mode="flags", tile=None):
    """Draw a snapshot with flags clipped to each area (mode 'flags') or the flags' main colours (mode 'colours')."""
    for f, rings in parts(year, tol):
        o = f["owner"]
        e = EM.get(f"{o}|{year}", {"kind": "none"}) if o else {"kind": "none"}
        pth = ppath(rings)
        k = e["kind"]
        if k in ("flag", "arms"):
            m = FM[e["file"]]; col = m["col"] if k == "flag" else mix(LAND, m["col"], .45)
            patch = PathPatch(pth, fc=col, ec="none", lw=0, zorder=1); ax.add_patch(patch)
            if mode == "flags":
                xs, ys = rings[0][:, 0], rings[0][:, 1]
                x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max(); bw, bh = x1 - x0, y1 - y0
                im = flagimg(m["id"]); ar = im.shape[1] / im.shape[0]
                if bw > 2e4 and bh > 2e4:
                    if k == "arms":
                        w = .5 * min(bw, bh * ar); h = w / ar; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                        art = ax.imshow(im, extent=(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2), zorder=2, interpolation="bilinear")
                    else:
                        w = max(bw, bh * ar); h = w / ar
                        if tile and w > tile:
                            w = tile; h = w / ar
                            for xx in np.arange(x0, x1, w):
                                for yy in np.arange(y0, y1, h):
                                    a = ax.imshow(im, extent=(xx, xx + w, yy, yy + h), zorder=2, interpolation="bilinear"); a.set_clip_path(patch)
                            art = None
                        else:
                            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                            art = ax.imshow(im, extent=(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2), zorder=2, interpolation="bilinear")
                    if art is not None:
                        art.set_clip_path(patch)
        elif k == "plain":
            ax.add_patch(PathPatch(pth, fc=PC.get(o, "#C9A27E"), ec="none", zorder=1))
        elif k in ("people", "group"):
            ax.add_patch(PathPatch(pth, fc=mix(LAND, KC[k][1], .55), ec=KC[k][1], lw=0, hatch="////" if k == "people" else "....", zorder=1))
        else:
            ax.add_patch(PathPatch(pth, fc=LAND, ec="none", zorder=1))
        ax.add_patch(PathPatch(pth, fc="none", ec=ec, lw=lw * (0.5 if k == "people" else 1), zorder=3))
    ax.set_aspect("equal"); ax.axis("off")
    if ext:
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    else:
        ax.set_xlim(-1.62e7, 1.62e7); ax.set_ylim(-6.6e6, 8.5e6)


def xy(lon, lat):
    return tr.transform(np.asarray(lon), np.asarray(lat))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
