# Who held the map?

Twelve centuries of the world map in flags: 30 snapshots from 800 to 2010, each area filled with the flag of whoever held it at that date, from the historical-basemaps world maps and Wikidata. Where no flag fits the year the map says so: a coat of arms, a plain colour, or a neutral hatch for peoples and cultural regions.

Interactive page: https://maps.tristanhotham.com/flags-through-time/
Paper: https://doi.org/10.5281/zenodo.23845995
Blog post: https://blog.tristanhotham.com/2026/10/31/flags-through-time/

## Headline results

- The share of the world's land that can honestly be filled with a flag in use: 0% in 1000, 3.7% in 1500, 40.9% in 1800, 74.8% in 1900 and 97.3% in 2010. It first passes half in 1878.
- The largest single entry in the basemap is the Mongol Empire in 1279 (20.5% of the world's land), the largest contiguous land empire on the map. Counting only the United Kingdom and its self-governing dominions, the British Empire in 1914 was larger (24.1%). From 1600 the largest single entry in every snapshot is Russia (Muscovy, the Russian Empire, the USSR), peaking at 22.1 million km2 in 1945.
- European states held 4.9% of the world's land in 1492 and 46.1% in 1914 (Russia included; 29.9% without). The United Kingdom's own land peaks at 11.0% in 1914, 24.1% with the dominions.
- Of 680 states, 535 (78.7%) matched a Wikidata item, covering 94.2% of the land they held; 42% of state-years get a flag, 42% of those from undated statements.
- For 93 of 194 present-day countries Wikidata dates the current flag; median start year 1986, often a re-specification rather than a new design.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/06_build_site.py`); loads `data/site.json`, `data/maps/<year>.json`, `data/flags/*.png` and `data/borders_today.json`. |
| `header.png` | Social card, 1200 x 630. |
| `data/maps/<year>.json` | 30 simplified snapshots (TopoJSON; 5.0 MB in all), each area with its name, holder, border precision, land area and label point. GPL-3.0. |
| `data/areas.csv` | Every area in every snapshot: name, SUBJECTO, holder, class, border precision, land, emblem, its dates and basis, Wikidata item (1.0 MB). GPL-3.0. |
| `data/entities.csv` | Every holder and snapshot: class, land, share of the world, emblem, Wikidata item and how it was matched. |
| `data/flag_credits.csv` | Every flag and coat of arms image used, its source page on Wikimedia Commons (or flag-icons) and licence. |
| `data/flags/` | The 413 images used, 160 px wide (2.8 MB). Each keeps its own licence. |
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
- Wikidata: items with the same English label or alias, chosen per snapshot year by lifespan and sitelinks; 76 holders set by hand by period (code/overrides.py).
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

Hotham, T. (2026) Who held the map? Twelve centuries of the world in flags, 800 to 2010, from historical basemaps and Wikidata. Zenodo. https://doi.org/10.5281/zenodo.23845995

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
