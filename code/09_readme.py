"""README.md, LICENSE and data/LICENSE, numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
m, fa, e = R["match"], R["flag_age"], R["emblems"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
msize = sum(os.path.getsize(os.path.join(MAPS, f)) for f in os.listdir(MAPS)) / 1e6
fsize = sum(os.path.getsize(os.path.join(FLAGDIR, f)) for f in os.listdir(FLAGDIR)) / 1e6
readme = f"""# Who held the map?

Twelve centuries of the world map in flags: {R['n_snapshots']} snapshots from 800 to 2010, each area filled with the flag of whoever held it at that date, from the historical-basemaps world maps and Wikidata. Where no flag fits the year the map says so: a coat of arms, a plain colour, or a neutral hatch for peoples and cultural regions.

Interactive page: {URL}
Paper: {{{{DOI_URL}}}}
Blog post: {{{{BLOG_URL}}}}

## Headline results

- The share of the world's land that can honestly be filled with a flag in use: 0% in 1000, {R['flag_share_1500']}% in 1500, {R['flag_share_1800']}% in 1800, {R['flag_share_1900']}% in 1900 and {R['flag_share_2010']}% in 2010. It first passes half in {R['first_flag_half']}.
- The largest single entry in the basemap is the {R['largest_ever']['n']} in {R['largest_ever']['y']} ({R['largest_ever']['pct']}% of the world's land), the largest contiguous land empire on the map. Counting only the United Kingdom and its self-governing dominions, the British Empire in {R['uk_dom_peak']['y']} was larger ({R['uk_dom_peak']['pct']}%). From 1600 the largest single entry in every snapshot is Russia (Muscovy, the Russian Empire, the USSR), peaking at {R['russia_peak']['a'] / 1e6:.1f} million km2 in {R['russia_peak']['y']}.
- European states held {R['euro_1492']['all']}% of the world's land in 1492 and {R['euro_peak']['all']}% in {R['euro_peak']['y']} (Russia included; {R['euro_peak_ex_russia']['v']}% without). The United Kingdom's own land peaks at {R['uk_peak']['pct']}% in {R['uk_peak']['y']}, {R['uk_dom_peak']['pct']}% with the dominions.
- Of {m['n_state']} states, {m['n_state_matched']} ({m['rate']}%) matched a Wikidata item, covering {m['rate_area']}% of the land they held; {e['flag_pct']}% of state-years get a flag, {e['undated_pct_of_flags']}% of those from undated statements.
- For {fa['n_dated']} of {fa['n_countries']} present-day countries Wikidata dates the current flag; median start year {fa['median']}, often a re-specification rather than a new design.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`); loads `data/site.json`, `data/maps/<year>.json`, `data/flags/*.png` and `data/borders_today.json`. |
| `header.png` | Social card, 1200 x 630. |
| `data/maps/<year>.json` | {R['n_snapshots']} simplified snapshots (TopoJSON; {msize:.1f} MB in all), each area with its name, holder, border precision, land area and label point. GPL-3.0. |
| `data/areas.csv` | Every area in every snapshot: name, SUBJECTO, holder, class, border precision, land, emblem, its dates and basis, Wikidata item ({size('areas.csv')}). GPL-3.0. |
| `data/entities.csv` | Every holder and snapshot: class, land, share of the world, emblem, Wikidata item and how it was matched. |
| `data/flag_credits.csv` | Every flag and coat of arms image used, its source page on Wikimedia Commons (or flag-icons) and licence. |
| `data/flags/` | The {R['images']['n']} images used, 160 px wide ({fsize:.1f} MB). Each keeps its own licence. |
| `data/flag_age.csv` | Present-day countries, their current flag in Wikidata and its start year where recorded. |
| `data/city_histories.csv` | Holder and emblem of sixteen cities at each snapshot. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/cities.json`, `data/borders_today.json` | Page tables; present-day city names and borders (Natural Earth). |
| `code/` | Scripts, run in order (below), page, paper and blog templates, `overrides.py` (all manual choices). |
| `release/` | Paper PDF and LaTeX source, blog figures and post, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Holders: SUBJECTO of each basemap area, spelling variants joined, a trailing "(UK)", "(France)" and so on read as the colonial power; two labelling errors in the 1930 map corrected (code/02_match.py). Land measured on a 0.1 degree equal-area grid, overlaps counted once, Antarctica excluded.
- Classes: peoples and cultural regions and loose groups of states are never given a flag (hatched); everything else is a state.
- Wikidata: items with the same English label or alias, chosen per snapshot year by lifespan and sitelinks; {m['n_overrides']} holders set by hand by period (code/overrides.py).
- Emblem rules: (1) a flag whose dates (qualifiers or file name) cover the year; (2) an undated flag of a historical state within its lifetime and from 1150, or of a present-day state from 1900 (Denmark from 1400, Sweden from 1600); (3) a coat of arms of a historical state under 400 years old within its lifetime from 1150, or dated arms; (4) plain colour. Fictitious, conjectural and unofficial files are never used. Never an invented flag.
- Flag ages: the open-ended P41 statement with the latest start date for each Natural Earth sovereign country.
- Caveats: simplified and disputed borders, especially before 1500; uneven detail between snapshots; flags only as recorded in Wikidata; automatic matching for small holders.

## How to rerun

Needs Python 3 with shapely, pyproj, rasterio, matplotlib, fontTools and Pillow; mapshaper (npm); node with playwright (for the two flag-icons renders and QA); xelatex and pdftotext. Raw inputs are read in place (paths in `code/common.py`): `historical-basemaps/geojson/world_<year>.geojson`, `flags/hb_wikidata.tsv`, `flags/flag_index.json`, `flags/png/`, Natural Earth countries and populated places. Intermediate files go to `/dev/shm/flags` (set `FLAGSTMP` to change).

```
python3 code/01_parse.py        # snapshots, land on an equal-area grid
python3 code/02_match.py        # holders, classes, Wikidata items, emblems
python3 code/03_flags.py        # images used, colours, credits
python3 code/04_geo.py          # web maps, page tables, areas.csv
python3 code/05_results.py      # results.json and tables
python3 code/06_build_site.py   # index.html
python3 code/07_figures.py      # header, paper and blog figures
python3 code/08_paper.py        # paper PDF
python3 code/09_readme.py       # README and licences
python3 code/10_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
python3 code/11_post.py         # reddit post text
node code/12_qa.js              # screenshots and console check
```

## Sources and licences

- historical-basemaps, Aleš Ourednik and contributors, https://github.com/aourednik/historical-basemaps. GPL-3.0. The derived boundary data (data/maps, data/areas.csv) are GPL-3.0 too: see data/LICENSE.
- Wikidata (flags P41 with start and end times, coats of arms P94, inception, dissolution, sitelinks), via QLever. CC0.
- Wikimedia Commons images: public domain, CC0, CC BY and CC BY-SA, each listed in data/flag_credits.csv.
- flag-icons by Panayiotis Lipiridis (MIT), for the flags of the People's Republic of China and North Korea.
- Natural Earth (public domain). Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Who held the map? Twelve centuries of the world in flags, 800 to 2010, from historical basemaps and Wikidata. Zenodo. {{{{DOI_URL}}}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
check_dashes(readme.replace("|---|---|", ""), "readme")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
mit = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/ and the page scripts. Other parts:

- data/maps/ and data/areas.csv derive from historical-basemaps by Ales Ourednik
  and contributors and are released under the GNU General Public License v3.0
  (see data/LICENSE).
- data/flags/ holds images from Wikimedia Commons, each under its own licence
  (public domain, CC0, CC BY or CC BY-SA), listed with its source page in
  data/flag_credits.csv; two images from flag-icons (MIT).
- The text of the page, the figures (which include flag images, some CC BY-SA)
  and the other data files are released under CC BY-SA 4.0. Wikidata is CC0;
  Natural Earth is public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(mit)
gpl = open(f"{HB}/LICENSE", encoding="utf-8").read()
open(os.path.join(DATA, "LICENSE"), "w", encoding="utf-8").write(
    "The boundary data in data/maps/ and the tables data/areas.csv and data/entities.csv are derived from\n"
    "historical-basemaps (https://github.com/aourednik/historical-basemaps), Copyright Ales Ourednik and\n"
    "contributors, and are released under the GNU General Public License version 3, reproduced below.\n"
    "Changes: geometries simplified (mapshaper, Visvalingam, 20% of points) and quantised; holders joined,\n"
    "classified and matched to Wikidata; two 1930 labels corrected (see code/02_match.py).\n"
    "Flag images in data/flags/ keep their own licences (data/flag_credits.csv).\n\n" + gpl)
print("README", len(readme.split()), "words")
