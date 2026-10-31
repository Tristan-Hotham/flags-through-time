"""Static figures: header.png (1200 x 630), paper figures (release/paper/f_*.png) and blog figures (release/blog/b_*.png).
All numbers from data/results.json; maps drawn from the snapshots with flags clipped to each area (figstyle.world_flags)."""
import shutil
from matplotlib.patches import Patch, Rectangle
from figstyle import *

R = jload(f"{DATA}/results.json")
PAP = os.path.join(ROOT, "release", "paper"); BLG = os.path.join(ROOT, "release", "blog")
os.makedirs(PAP, exist_ok=True); os.makedirs(BLG, exist_ok=True)
YS = R["years"]
SIX = [1200, 1500, 1700, 1815, 1914, 2010]


def legend_handles():
    return [Patch(fc=KC["flag"][1], label="Flag in use that year"), Patch(fc=mix(LAND, KC["arms"][1], .45), label="Coat of arms or royal banner"),
            Patch(fc="#C9A27E", label="State, no flag recorded"), Patch(fc=mix(LAND, KC["people"][1], .55), hatch="////", ec=KC["people"][1], lw=0, label="People or cultural region"),
            Patch(fc=mix(LAND, KC["group"][1], .55), hatch="....", ec=KC["group"][1], lw=0, label="Group of small states"), Patch(fc=LAND, label="No holder named")]


def fig_multiples(path, years=SIX, cols=2, w=12, title=True):
    rows = (len(years) + cols - 1) // cols
    fig = plt.figure(figsize=(w, rows * w / cols * .52 + 1.1), facecolor=BG)
    H = rows * w / cols * .52 + 1.1
    for i, y in enumerate(years):
        r, c = divmod(i, cols)
        ax = fig.add_axes([c / cols + .005, 1 - (r + 1) * (w / cols * .52) / H - .02, 1 / cols - .01, (w / cols * .5) / H])
        world_flags(ax, y, lw=.18)
        cv = [d for d in R["cover"] if d["y"] == y][0]
        ax.text(-1.55e7, -5.6e6, str(y), fontproperties=DISP, fontsize=26, color=FG)
        ax.text(-1.55e7, -6.5e6, f"{cv['flag']:.0f}% of land under a flag in use", fontsize=9.5, color=MUT)
    fig.legend(handles=legend_handles(), loc="lower center", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(.5, .0))
    save(fig, path, dpi=170)


def fig_europe(path, year=1600):
    fig = plt.figure(figsize=(10, 7.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, .94])
    x0, y0 = xy(-11, 35.5); x1, y1 = xy(42, 61)
    world_flags(ax, year, ext=(x0, x1, y0, y1), lw=.5, tol=.02, tile=6.5e5)
    fig.text(.02, .975, f"Europe in {year}, in flags", fontproperties=DISP, fontsize=22, color=FG, va="top")
    save(fig, path, dpi=170)


def fig_cover(path):
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=BG); ax.set_facecolor(BG)
    ys = [d["y"] for d in R["cover"]]; keys = ["flag", "arms", "plain", "group", "people", "none"]
    ax.stackplot(ys, [[d[k] for d in R["cover"]] for k in keys], colors=[KC[k][1] for k in keys], labels=[KC[k][0] for k in keys], edgecolor=BG, lw=.5)
    ax.set_xlim(800, 2010); ax.set_ylim(0, 100); ax.set_ylabel("Share of the world's land (%)")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    h, l = ax.get_legend_handles_labels(); ax.legend(h[::-1], l[::-1], loc="upper left", frameon=False, fontsize=9.5)
    for y in ys: ax.axvline(y, color=FG, alpha=.08, lw=.6)
    fig.tight_layout(); save(fig, path)


def fig_largest(path):
    rows = R["largest_by_year"]; n = len(rows)
    fig = plt.figure(figsize=(10, 9.6), facecolor=BG); ax = fig.add_axes([.27, .04, .66, .92]); ax.set_facecolor(BG)
    mx = max(r["pct"] for r in rows)
    for i, r in enumerate(rows):
        e = EM[f"{r['n']}|{r['y']}"]
        col = KC["flag"][1] if e["kind"] == "flag" else KC["plain"][1]
        ax.barh(i, r["pct"], color=col, height=.72)
        ax.text(r["pct"] + .25, i, f"{r['pct']:.1f}%", va="center", fontsize=9, color=MUT)
        fig.text(.005, 1 - (.04 + (i + .5) * .92 / n), f"{r['y']}", fontsize=9.5, color=MUT, va="center")
        fig.text(.105, 1 - (.04 + (i + .5) * .92 / n), r["n"], fontsize=9.5, color=FG, va="center")
        if e.get("file"):
            im = flagimg(FM[e["file"]]["id"]); axi = fig.add_axes([.055, 1 - (.04 + (i + .88) * .92 / n), .042, .92 / n * .76]); axi.imshow(im, aspect="auto"); axi.axis("off")
    ax.set_ylim(n - .5, -.5); ax.set_xlim(0, mx * 1.12); ax.set_yticks([])
    ax.set_xlabel("Share of the world's land held (%)")
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    save(fig, path)


def fig_euro(path):
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG); ax.set_facecolor(BG)
    E = R["euro"]; ys = [d["y"] for d in E]
    ax.stackplot(ys, [[d[k] for d in E] for k in ("home", "overseas", "russia")], colors=[COOL, HOT, "#8E9AAE"],
                 labels=["Other European states, in Europe", "Other European states, outside Europe", "Muscovy, Russian Empire and USSR (all land)"], edgecolor=BG, lw=.5)
    ax.set_xlim(1492, 2010); ax.set_ylim(0, 50); ax.set_ylabel("Share of the world's land (%)")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    for y in ys: ax.axvline(y, color=FG, alpha=.08, lw=.6)
    fig.tight_layout(); save(fig, path)


def fig_cities(path):
    C = R["cities"]; n = len(YS)
    fig = plt.figure(figsize=(12, 6.4), facecolor=BG); ax = fig.add_axes([.1, .03, .89, .9]); ax.set_facecolor(BG)
    for ci, c in enumerate(C):
        for i, h in enumerate(c["h"]):
            if h["f"]:
                ax.imshow(flagimg(h["f"]), extent=(i + .04, i + .96, ci + .86, ci + .14), aspect="auto", zorder=2)
            else:
                k = h["k"]; fc = PC.get(h["o"], "#C9A27E") if k == "plain" else (mix(LAND, KC[k][1], .55) if k in ("people", "group") else LAND)
                ax.add_patch(Rectangle((i + .04, ci + .14), .92, .72, fc=fc, ec="none", hatch="////" if k == "people" else None, zorder=2))
        ax.text(-.3, ci + .5, c["c"], ha="right", va="center", fontsize=10)
    ax.set_xlim(0, n); ax.set_ylim(len(C), 0); ax.axis("off")
    for i, y in enumerate(YS):
        if i % 3 == 0 or i == n - 1: ax.text(i + .5, -.25, str(y), ha="center", fontsize=8.5, color=MUT)
    save(fig, path)


def fig_states(path):
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
    E = R["entities"]; ys = [d["y"] for d in E]
    ax.plot(ys, [d["states"] for d in E], "-o", color=COOL, ms=3.5, label="States")
    ax.plot(ys, [min(d["people"], 600) for d in E], "-o", color=KC["people"][1], ms=3.5, label="Peoples and cultural regions (1492 cut at 600)")
    ax.set_xlim(800, 2010); ax.set_ylim(0, 620); ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_ylabel("Distinct holders named"); fig.tight_layout(); save(fig, path)


def fig_age(path):
    B = R["flag_age"]["bins"]
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=BG); ax.set_facecolor(BG)
    ax.bar([b["b"] + 10 for b in B], [b["n"] for b in B], width=17, color=[HOT if b["b"] >= 1945 else COOL for b in B])
    for b in B: ax.text(b["b"] + 10, b["n"] + .4, str(b["n"]), ha="center", fontsize=9)
    ax.set_xticks([b["b"] + 10 for b in B]); ax.set_xticklabels([f"{b['b']}s" for b in B], fontsize=8.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_ylabel("Present-day countries")
    ax.set_title(f"{R['flag_age']['n_dated']} of {R['flag_age']['n_countries']} countries have a start date in Wikidata for their current flag", fontsize=10, color=MUT, loc="left")
    fig.tight_layout(); save(fig, path)


def header(path):
    fig = plt.figure(figsize=(12, 6.3), facecolor=BG)
    ax = fig.add_axes([.36, .06, .64, .88]); world_flags(ax, 1914, lw=.15)
    fig.text(.04, .86, "Who held\nthe map?", fontproperties=DISP, fontsize=50, color=FG, va="top", linespacing=.95)
    fig.text(.04, .45, "The world in flags,\n800 to 2010", fontproperties=SERP, fontsize=19, color=FG, va="top")
    fig.text(.04, .26, f"{R['flag_share_1500']:.1f}% of land under a flag in 1500\n{R['flag_share_2010']:.0f}% in 2010", fontsize=12, color=HOT, va="top", linespacing=1.5)
    fig.text(.04, .07, "maps.tristanhotham.com/flags-through-time", fontsize=10, color=MUT)
    fig.text(.985, .04, "1914", fontproperties=DISP, fontsize=22, color=FG, ha="right")
    save(fig, path, dpi=100)


if __name__ == "__main__":
    header(os.path.join(ROOT, "header.png"))
    fig_multiples(f"{PAP}/f_multiples.png"); fig_europe(f"{PAP}/f_europe1600.png"); fig_cover(f"{PAP}/f_cover.png"); fig_largest(f"{PAP}/f_largest.png")
    fig_euro(f"{PAP}/f_euro.png"); fig_cities(f"{PAP}/f_cities.png"); fig_states(f"{PAP}/f_states.png"); fig_age(f"{PAP}/f_age.png")
    for a, b in (("f_multiples", "b_multiples"), ("f_europe1600", "b_europe1600"), ("f_cover", "b_cover"), ("f_largest", "b_largest"),
                 ("f_euro", "b_euro"), ("f_cities", "b_cities"), ("f_age", "b_age")):
        shutil.copy(f"{PAP}/{a}.png", f"{BLG}/{b}.png")
    from PIL import Image
    assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
    print("figures done")
