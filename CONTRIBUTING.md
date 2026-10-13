# Adding a context layer

A context layer lights up a set of buildings that share a piece of history, and tells why each one is there.
There are two kinds. Pick the one that fits, open a pull request, and describe the layer in a sentence or two.

## 1. A hand-picked layer (most contributions)

Add an entry to `CURATED` in [`pipeline/curated.py`](pipeline/curated.py):

```python
CURATED.append(dict(
    id="markets", section="Trade and industry", title="Markets", era="1600–today",
    intro="Two or three sentences on the history behind the layer.",
    entries=[
        # (name, address, story, "lang:Wikipedia title", (facts the article must contain), group)
        ("Waag", "Markt 11",
         "The town weigh house, where weighing went on until 1960.",
         "nl:Waag (Delft)", ("1960",), "markets"),
    ]))
```

Rules, checked by `uv run python -m pipeline.s08_curated`:

- **Every story rests on a Wikipedia article.** The checks are strings that must appear in it: a year, a name, a key word.
  If the article does not say it, the story should not either.
- **The address is a current Delft address** with its house number. It is matched to its BAG building through the BAG address
  register; when the article is about the building itself and its Wikidata item is placed on a building, that one is used.
- **Stories are short and plain:** one or two sentences, what happened and when. Legends are named as legends.
- **No personal data about private people.** Public figures are fine.

The script prints `layer n/m` and every entry it dropped with the reason. A layer needs five to ten buildings or more;
smaller sets fit better in an existing layer.

Add the Dutch version of every new text to [`pipeline/i18n_nl_delft.json`](pipeline/i18n_nl_delft.json); `s05_layers` lists any text
still missing a translation.

## 2. A layer from an open dataset

Add a function to [`pipeline/layers.py`](pipeline/layers.py) with the `@layer(...)` decorator. It returns
`{BAG pand id: group}` or `{BAG pand id: (group, {"story": ...})}`. Helpers are there for the common joins:
`within(polygons, column)`, `near_points(points, column, radius)` and `by_monument({monument number: group})`.
Add a download step for the dataset in `pipeline/s00_fetch_layers.py` and say which licence it carries;
only openly licensed data can go in.

## Checking your layer

```bash
uv run python -m pipeline.s08_curated   # hand-picked layers
uv run python -m pipeline.s05_layers    # counts per group, missing translations
uv run python -m pipeline.s03_tiles
python3 -m http.server 8642 --directory web
```

## 3. A quest

A quest is a chain of riddles; each one is solved by finding a building on the map. Add it to `QUESTS` in
[`pipeline/quests.py`](pipeline/quests.py). Build riddles on facts the map already carries (a story of a context layer,
a 'Did you know' fact, a year or a layer group), give each a hint that names a street or a layer, and run
`uv run python -m pipeline.s12_quests` to check every answer resolves to buildings.
