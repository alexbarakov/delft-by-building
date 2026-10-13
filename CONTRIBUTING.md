# Adding a context layer

A context layer lights up a set of buildings that share a piece of history, and tells why each one is there.
There are two kinds. Pick the one that fits, open a pull request, and describe the layer in a sentence or two.

## 1. A hand-picked layer (most contributions)

Add an entry to `CURATED` in [`pipeline/curated.py`](pipeline/curated.py):

```python
CURATED.append(dict(
    id="markets", title="Markets", era="1600–today",
    intro="Two or three sentences on the history behind the layer.",
    entries=[
        # (name, address, story, "lang:Wikipedia title", (facts the article must contain), group)
        ("Waag", "Nieuwmarkt 4",
         "A city gate of 1488 that became a weighhouse for the market around it.",
         "nl:Waag (Amsterdam)", ("1488",), "markets"),
    ]))
```

Rules, checked by `uv run python -m pipeline.s08_curated`:

- **Every story rests on a Wikipedia article.** The checks are strings that must appear in it: a year, a name, a key word.
  If the article does not say it, the story should not either.
- **The address is a current Amsterdam address** with its house number. It is geocoded to a BAG building; when the
  article is about the building itself and Wikidata gives its BAG id, that id is used instead.
- **Stories are short and plain:** one or two sentences, what happened and when. Legends are named as legends.
- **No personal data about private people.** Public figures are fine.

The script prints `layer n/m` and every entry it dropped with the reason. A layer needs about ten buildings or more;
smaller sets fit better as a group in an existing layer, such as *The world in Amsterdam*.

Add the Dutch version of every new text to [`pipeline/i18n_nl.py`](pipeline/i18n_nl.py); `s05_layers` lists any text
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
