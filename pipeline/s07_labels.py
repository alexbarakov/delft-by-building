"""Street and canal names, placed along their own outlines.

Source: named streets, canals and squares from OpenStreetMap (ODbL), fetched to data/raw/osm_names.json.
A street line is widened by its class into a band; canals and squares keep their own outline. Each outline
is cut into 300 m cells; every piece longer than it is wide gets one label at its centre, turned along its
long side. Tier 1 (canals and main streets) shows from afar, tier 2 only up close.
"""
import json
import math
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, box

from .s03_tiles import DAM

CELL = 300.0
WIDTH = {"trunk": 22, "primary": 18, "secondary": 14, "tertiary": 11, "unclassified": 9, "residential": 9,
         "living_street": 7, "pedestrian": 8, "busway": 8, "canal": 12, "river": 30, "stream": 6}
TIER1 = {
    # canals and rivers
    "Oude Delft", "Koornmarkt", "Wijnhaven", "Voldersgracht", "Oosteinde", "Verwersdijk", "Oude Langendijk",
    "Nieuwe Langendijk", "Hippolytusbuurt", "Binnenwatersloot", "Rietveld", "Oostsingel", "Zuidwal",
    "Noordeinde", "Delftse Schie", "Rijn-Schiekanaal", "Schie", "Kolk", "Buitenwatersloot", "Westsingelgracht",
    "Noordwest Buitensingel", "Achterom",
    # main streets and squares
    "Markt", "Beestenmarkt", "Brabantse Turfmarkt", "Choorstraat", "Breestraat", "Phoenixstraat", "Westvest",
    "Oostpoortweg", "Rotterdamseweg", "Schoemakerstraat", "Mekelweg", "Kanaalweg", "Papsouwselaan",
    "Kruithuisweg", "Westlandseweg", "Provinciale Weg", "Martinus Nijhofflaan", "Julianalaan", "Jaffalaan",
    "Hugo de Grootstraat", "Van Foreestweg", "Ruys de Beerenbrouckstraat", "Sint Sebastiaansbrug",
    "Coenderstraat", "Laan van Altena", "Abtswoudseweg", "Vulcanusweg", "Schieweg",
}


def outlines():
    """(name, is water, polygon) for every named OSM element."""
    for e in json.load(open("data/raw/osm_names.json"))["elements"]:
        tags = e["tags"]
        name = tags["name"]
        water = "waterway" in tags or tags.get("natural") == "water"
        kind = tags.get("highway") or tags.get("waterway")
        if e["type"] == "way":
            xy = [(p["lon"], p["lat"]) for p in e["geometry"]]
            closed = len(xy) > 3 and xy[0] == xy[-1]
            area = tags.get("natural") == "water" or tags.get("place") == "square" or tags.get("area") == "yes"
            if closed and area:
                yield name, water, to_rd(Polygon(xy))
            elif kind in WIDTH:
                yield name, water, to_rd(LineString(xy)).buffer(WIDTH[kind] / 2, cap_style="flat")
        elif e["type"] == "relation":
            rings = [to_rd(Polygon([(p["lon"], p["lat"]) for p in m["geometry"]]))
                     for m in e.get("members", []) if m.get("role") == "outer" and m.get("geometry")
                     and len(m["geometry"]) > 3 and m["geometry"][0] == m["geometry"][-1]]
            if rings:
                yield name, water, shapely.union_all(rings)


_T = __import__("pyproj").Transformer.from_crs(4326, 28992, always_xy=True)


def to_rd(g):
    return shapely.transform(g, lambda c: np.c_[_T.transform(c[:, 0], c[:, 1])])


def pieces(geom):
    x0, y0, x1, y1 = geom.bounds
    for cx in np.arange(math.floor(x0 / CELL) * CELL, x1, CELL):
        for cy in np.arange(math.floor(y0 / CELL) * CELL, y1, CELL):
            part = geom.intersection(box(cx, cy, cx + CELL, cy + CELL))
            for p in getattr(part, "geoms", [part]):
                if p.geom_type == "Polygon" and p.area > 200:
                    yield p


def placement(p):
    """Centre and angle (degrees, local frame) of a piece, or None if it is not elongated."""
    r = p.minimum_rotated_rectangle
    c = np.array(r.exterior.coords)[:4]
    e1, e2 = c[1] - c[0], c[2] - c[1]
    long, short = (e1, e2) if np.hypot(*e1) >= np.hypot(*e2) else (e2, e1)
    if np.hypot(*long) < 2.2 * np.hypot(*short) or np.hypot(*long) < 60:
        return None
    pt = p.representative_point() if not p.contains(p.centroid) else p.centroid
    ang = math.degrees(math.atan2(-long[1], long[0]))  # local z points south
    ang = (ang + 90) % 180 - 90  # keep text upright
    # The piece's width: area over length is the street's mean width, steadier than the rectangle's short side.
    width = p.area / max(np.hypot(*long), 1)
    return [round(pt.x - DAM[0], 1), round(-(pt.y - DAM[1]), 1), round(ang, 1), round(float(np.hypot(*long))),
            round(float(width), 1)]


def main():
    by_name = {}
    for name, water, g in outlines():
        w, gs = by_name.setdefault(name, [False, []])
        by_name[name] = [w or water, gs + [shapely.make_valid(g)]]
    labels = []
    for name, (water, gs) in by_name.items():
        pts = [pl for p in pieces(shapely.union_all(gs)) if (pl := placement(p))]
        if pts:
            labels.append(dict(name=name, water=water, tier=1 if name in TIER1 else 2, pts=pts))
    # One entry per name: a canal is registered both as water and as the street along it; keep the water.
    merged = {}
    for l in sorted(labels, key=lambda l: not l["water"]):
        m = merged.setdefault(l["name"], dict(l, pts=[]))
        m["pts"] += l["pts"]
    labels = []
    for m in merged.values():
        # Keep placements at least 350 m apart, longest stretches first.
        kept = []
        for p in sorted(m["pts"], key=lambda p: -p[3]):
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 350 ** 2 for q in kept):
                kept.append(p)
        m["pts"] = kept
        labels.append(m)
    Path("web/data/labels.json").write_text(json.dumps(labels, ensure_ascii=False, separators=(",", ":")))
    print(len(labels), "names,", sum(len(l["pts"]) for l in labels), "placements,",
          sum(l["tier"] == 1 for l in labels), "tier 1;", Path("web/data/labels.json").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
