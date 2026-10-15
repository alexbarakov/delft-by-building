# Delft, building by building

Every building standing in Delft today, 37,000 of them, by age and historical context.
**Live:** https://stop-token.com/lab/delft/

A sibling of [LAYRS: Amsterdam](https://github.com/alexbarakov/amsterdam-by-building): the same pipeline, with the
city-specific parts in `pipeline/city.py`.

A non-commercial project, made for curiosity and learning. Inspired by Sasha Bogachev's
[Paris, building by building](https://paris.bogachev.fr); the architecture, a data pipeline feeding a three.js city, follows his.

**Want to add a layer?** See [CONTRIBUTING.md](CONTRIBUTING.md). A layer can be a hand-picked list of buildings with a story
each, or a rule over an open dataset.

## How it works

```
open data ──► pipeline/ (Python) ──► web/data/ (binary tiles + JSON) ──► web/ (three.js, no build step)
```

| Step | What it does |
|---|---|
| `s00_fetch_*` | Downloads the RCE and Wikidata registers, every BAG address, BGT water, OSM street names, energy labels |
| `s01c_roofs` | LoD 2.2 roof faces per building; the viewer raises the walls from their open edges |
| `s01d_spires` | Towers and spires above the model, as 0.5 m columns from the AHN surface model |
| `s01b_monuments` | Links each national monument to its buildings: by the addresses RCE registers, else by its outline |
| `s01_load` | 3D BAG tiles → buildings and their LoD 1.3 parts |
| `s02_attributes` | Cleans construction years (placeholders, rounded years, monument register), floors, heights |
| `s03_tiles` | Packs 600 m tiles into 8 bundles, writes per-building attributes and the city config |
| `s04_water` | Water and land polygons |
| `s05_layers` | Resolves every context layer to a bit per building; adds Dutch texts |
| `s06_wiki` | Names, photos and extracts from Wikidata, Wikipedia and Commons |
| `s07_labels` | Street and canal names placed along their outlines |
| `s08_curated` | Checks hand-written stories against Wikipedia and geocodes them |
| `s09_residents` | Finds addresses of well-known residents in Dutch Wikipedia |
| `s10_commons` | Finds more building photos on Commons by address in the file name |
| `s13_search` | Search index (names, addresses, streets), street rows for 'side by side' and street-view eye points |
| `s12_quests` | Resolves the quests (chains of riddles in `pipeline/quests.py`) to their buildings |
| `s13_graph` | The ontology graph: people, events and organisations (`pipeline/ontology.py`) linked to buildings by checked stories; `web/graph.html` |

## Run it

```bash
uv sync
# raw inputs: the 3D BAG tiles listed in data/raw/tiles_needed.csv, the PDOK boundary, then the s00_* fetchers
for s in s00_fetch_registers s00_fetch_addresses s00_fetch_water s00_fetch_energy s01_load s01b_monuments \
         s02_attributes s01c_roofs s01d_spires s06_wiki s07_labels s08_curated s09_residents s10_commons s06_wiki s11_facts s05_layers s03_tiles s04_water s12_quests s13_graph s13_search; do
  uv run python -m pipeline.$s
done
python3 -m http.server 8644 --directory web
```

Raw downloads (`data/`) and generated output (`web/data/`) are not in the repository: they are large and rebuilt by the pipeline.

## Data decisions

- **Years.** In the old town BAG often gives a round year (1850, 1890, 1930) more often than the years around it
  predict. Round years before 1940 are spread across their rounding step and drawn paler. Where the national monument
  register (RCE) dates a building earlier than BAG, which often records a rebuilding, the register wins.
- **Stories.** Every hand-written story names its Wikipedia article; `s08_curated` checks that the article contains the
  story's key facts and the address, then geocodes the address to its BAG building. Entries that fail are dropped.

## Licence

Code: MIT (see [LICENSE](LICENSE)). Data keeps the licence of its source: 3D BAG CC BY 4.0; BAG, BGT, RCE, Wikidata and
street names from OpenStreetMap ODbL; Wikipedia text CC BY-SA;
Wikimedia Commons photos each under their own licence, credited in the app.
