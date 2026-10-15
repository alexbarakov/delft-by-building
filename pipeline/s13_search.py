"""Search index, street rows and street-level viewpoints (web/data/search.json).

streets: every street with its house numbers, each number pointing at its building (gid, the building's index in
  data/buildings.parquet, as in the tiles).
eyes: per building, a point on the street in front of it, for the street view.
  Per street also its buildings in a row: side (odd/even numbers), extent along the street's axis and offset
  across it, so the viewer can stand the two sides of a street side by side.
names: named buildings (Wikidata, context-layer stories) and well-known residents, each pointing at a building.
Coordinates are local metres (x east, z south of the origin), as everywhere in the viewer.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import shapely.ops
from shapely.geometry import LineString, Point

from .city import ORIGIN
from .s07_labels import to_rd

EYE_MIN, EYE_MAX = 12, 26  # metres from the house front: past the street's centre line, short of the far side
MAX_EYE_DIST = 45   # metres from the house to its street; farther, the house gets no street view


def local(x, y):
    return round(x - ORIGIN[0], 1), round(-(y - ORIGIN[1]), 1)


def street_lines():
    lines = defaultdict(list)
    for e in json.load(open("data/raw/osm_names.json"))["elements"]:
        t = e["tags"]
        if e["type"] == "way" and ("highway" in t or t.get("place") == "square"):
            lines[t["name"]].append(to_rd(LineString([(p["lon"], p["lat"]) for p in e["geometry"]])))
    return {k: shapely.union_all(v) for k, v in lines.items()}


def main():
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "geometry"])
    bag = b.identificatie.str.slice(-16).to_numpy()
    gid = {k: i for i, k in enumerate(bag)}
    geom = shapely.make_valid(b.geometry.values)
    cent = shapely.centroid(geom)
    lines = street_lines()
    every = shapely.union_all(list(lines.values()))
    sidx = shapely.STRtree(geom)

    def eye(g, street=None):
        """A point on the street in front of building g, between its front and the street's centre line."""
        line = lines.get(street) if street else None
        c = cent[g]
        if line is None or line.distance(c) > MAX_EYE_DIST:
            line = every
        on = shapely.ops.nearest_points(line, c)[0]
        if on.distance(c) > MAX_EYE_DIST:
            return None
        front = shapely.ops.nearest_points(geom[g].exterior if geom[g].geom_type == "Polygon" else geom[g], on)[0]
        dx, dy = on.x - front.x, on.y - front.y
        d = max(np.hypot(dx, dy), 0.1)
        # step back from the front, past the street's centre line, until clear of buildings
        for dist in (min(max(d * 1.4, EYE_MIN), EYE_MAX), d, d * 0.7, 4.0):
            x, y = front.x + dx / d * dist, front.y + dy / d * dist
            if not len(sidx.query(Point(x, y), predicate="within")):
                return local(x, y)
        return None

    by_street = defaultdict(dict)
    for a in json.load(open("data/raw/addresses.json")):
        g = gid.get(a["pandidentificatie"])
        if g is None:
            continue
        num = f'{a["huisnummer"]}{a["huisletter"] or ""}'
        # one entry per number; a plain number keeps its own building over its lettered neighbours
        by_street[a["openbare_ruimte"]].setdefault(num, (g, a["huisnummer"]))

    streets, eyes = [], {}
    for name, nums in sorted(by_street.items()):
        entries, gids = [], {}
        for num, (g, n) in sorted(nums.items(), key=lambda kv: (kv[1][1], kv[0])):
            if g not in eyes:
                eyes[g] = eye(g, name)
            entries.append([num, g])
            gids.setdefault(g, n)
        # the row: the street's axis is the main direction of its buildings' centres
        pts = np.array([[cent[g].x, cent[g].y] for g in gids])
        row = []
        if len(pts) >= 2:
            mid = pts.mean(axis=0)
            u, s, vt = np.linalg.svd(pts - mid, full_matrices=False)
            ax = vt[0]
            line = lines.get(name)
            # orient the axis so house numbers rise along it
            order = np.array([gids[g] for g in gids])
            if len(set(order)) > 1 and np.corrcoef((pts - mid) @ ax, order)[0, 1] < 0:
                ax = -ax
            perp = np.array([-ax[1], ax[0]])
            for g, n in gids.items():
                xy = shapely.get_coordinates(geom[g])
                t = (xy - mid) @ ax
                off = (np.array([cent[g].x, cent[g].y]) - mid) @ perp
                row.append([g, n % 2, round(float(t.min()), 1), round(float(t.max()), 1), round(float(off), 1)])
            cx, cz = local(*mid)
            streets.append(dict(n=name, a=entries, c=[cx, cz], ax=[round(float(ax[0]), 4), round(float(-ax[1]), 4)],
                                row=row))
        else:
            c = cent[next(iter(gids))]
            streets.append(dict(n=name, a=entries, c=list(local(c.x, c.y)), row=[]))

    names, seen = [], set()
    def add(label, label_nl, g, kind):
        k = (label.lower() if label else "", g)
        # Wikidata labels many listed houses by their address ('Oude Kerkstraat 6, Delft'): the address search finds those
        if kind == "building" and label and re.search(r"\d", label):
            return
        if label and g is not None and k not in seen:
            seen.add(k)
            if g not in eyes:
                eyes[g] = eye(g)
            names.append([label, label_nl if label_nl and label_nl != label else None, g, kind])

    wiki = json.load(open("web/data/wiki.json"))
    wk = pd.read_parquet("data/wiki_index.parquet")
    first = wk.groupby("wk").bag.first()
    for k, bg in first.items():
        w = wiki[k]
        if w.get("label"):
            add(w["label"], w.get("label_nl"), gid.get(bg), "building")
    for L in json.load(open("data/curated.json")):
        for e in L["entries"]:
            if not re.fullmatch(r".*\d+", e["name"]):  # 'Oude Delft 95' is an address, found as one
                add(e["name"], None, gid.get(e["bag"]), "building")
    for r in json.load(open("data/residents.json")):
        add(r["person"], None, gid.get(r["bag"]), "person")

    out = dict(streets=streets, names=names, eyes={g: e for g, e in eyes.items() if e})
    Path("web/data/search.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    n_addr = sum(len(s["a"]) for s in streets)
    print(f"{len(streets)} streets, {n_addr} numbers, {len(out['eyes'])} buildings with a street view, {len(names)} names; "
          f"{Path('web/data/search.json').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
