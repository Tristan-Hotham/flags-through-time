"""reddit/post.md: title, body and source comment, numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
t = f"""## Title

[OC] Who held the map? The world from 800 to 2010 with every area filled with its holder's flag, only where a flag in use that year is recorded: 0% of land in 1000, {R['flag_share_1500']}% in 1500, {R['flag_share_2010']:.0f}% in 2010

## Body

I joined the open historical-basemaps world maps ({R['n_snapshots']} dates from 800 to 2010) with flag statements and their dates in Wikidata, and filled each piece of land with the flag of whoever held it, but only when Wikidata records a flag that fits the year. Before about 1700 most states flew no national flag, so the old maps are mostly plain colours, coats of arms and hatching for peoples and cultural regions. The map passes half flags in {R['first_flag_half']}. The largest single entry in the basemap is the {R['largest_ever']['n']} in {R['largest_ever']['y']} ({R['largest_ever']['pct']}% of the world's land), though counting only the United Kingdom and its self-governing dominions the British Empire in {R['uk_dom_peak']['y']} was larger ({R['uk_dom_peak']['pct']}%); European states held {R['euro_peak']['all']}% in {R['euro_peak']['y']}, Russia included. Caveats: borders are simplified and approximate, especially before 1500, and the flags are only those Wikidata knows. Interactive version with a play button and a click-anywhere history: {URL}

## Source comment

Source: historical-basemaps by Aleš Ourednik and contributors (GPL-3.0), https://github.com/aourednik/historical-basemaps; flags (P41 with start and end dates) and coats of arms from Wikidata via QLever (CC0); {R['images']['n']} images from Wikimedia Commons (public domain, CC0, CC BY and CC BY-SA, each credited in data/flag_credits.csv); two present-day flags from flag-icons (MIT). No flag invented: flags marked fictitious or conjectural are never used.

Tools: Python (shapely, rasterio, matplotlib), mapshaper; Leaflet for the interactive map.

Interactive version: {URL}
Paper: {{{{DOI_URL}}}}
Blog post: {{{{BLOG_URL}}}}
"""
check_dashes(t, "post")
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(t)
print("post.md written")
