"""r/dataisbeautiful collage for flags-through-time: 2400 x 3000 px on a light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
from matplotlib.patches import Patch

R = jload(f"{DATA}/results.json")
BGc = "#F7F3EA"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGc)
fig.text(.045, .975, "Who held the map?", fontproperties=DISP, fontsize=60, color=FG, va="top")
fig.text(.045, .908, "The world from 800 to 2010, each piece of land filled with the flag of whoever held it,\n"
         "only where a flag in use that year is recorded. Everything else is shown as it was: without one.",
         fontproperties=SERP, fontsize=16, color=FG, va="top", linespacing=1.4)
years = [1000, 1492, 1700, 1815, 1914, 2010]
cov = {c["y"]: c for c in R["cover"]}
for i, y in enumerate(years):
    r, c = divmod(i, 2)
    ax = fig.add_axes([.02 + c * .49, .632 - r * .2, .47, .19])
    world_flags(ax, y, lw=.15)
    fig.text(.03 + c * .49, .683 - r * .2, str(y), fontproperties=DISP, fontsize=27, color=FG, va="top")
    fig.text(.03 + c * .49, .655 - r * .2, f"{cov[y]['flag']:.1f}% of land\nunder a flag in use", fontsize=10, color=MUT, va="top", linespacing=1.3)
leg = [Patch(fc=KC["flag"][1], label="Flag in use that year (drawn in the map)"), Patch(fc=mix(LAND, KC["arms"][1], .45), label="Coat of arms or royal banner"),
       Patch(fc="#C9A27E", label="State with no flag recorded for that year"), Patch(fc=mix(LAND, KC["people"][1], .55), hatch="////", ec=KC["people"][1], lw=0, label="People or cultural region (no flag drawn)"),
       Patch(fc=mix(LAND, KC["group"][1], .55), hatch="....", ec=KC["group"][1], lw=0, label="Group of small states"), Patch(fc=LAND, label="No holder named in the basemap")]
fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(.035, .232), ncol=2, frameon=False, fontsize=10.5, handlelength=1.4, columnspacing=2)
nums = [("0%", HOT, "of land can honestly be\nshown under a flag in\nthe year 1000"),
        (f"{R['flag_share_2010']:.0f}%", HOT, "of land under a flag in\nuse in 2010"),
        (f"{R['largest_ever']['pct']:.1f}%", COOL, f"held by the {R['largest_ever']['n']}\nin {R['largest_ever']['y']}, the largest\nsingle basemap entry. The\nBritish Empire with its\ndominions, {R['uk_dom_peak']['y']}: {R['uk_dom_peak']['pct']:.1f}%"),
        (f"{R['euro_peak']['all']:.0f}%", GOLD, f"of land held by European\nstates in {R['euro_peak']['y']} (Russia\nincluded)")]
for i, (big, col, txt) in enumerate(nums):
    x = .045 + i * .235
    fig.text(x, .174, big, fontproperties=DISP, fontsize=40, color=col, va="top")
    fig.text(x, .131, txt, fontsize=10, color=FG, va="top", linespacing=1.2)
fig.text(.045, .008, "Data: historical-basemaps, Aleš Ourednik and contributors (GPL-3.0); flags and dates: Wikidata (CC0); images: Wikimedia Commons\n"
         "(public domain, CC BY and CC BY-SA, each credited online). Borders are simplified and approximate, especially before 1500.\n"
         "Dr Tristan Hotham · maps.tristanhotham.com/flags-through-time", fontsize=9.6, color=MUT, va="bottom", linespacing=1.45)
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "who_held_the_map.png"), dpi=200, facecolor=BGc)
print("collage done")
