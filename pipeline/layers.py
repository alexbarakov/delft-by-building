"""Layers: historical contexts, each a set of buildings.

A layer has one or more groups; every group takes one bit of a 64-bit mask per building.
Each source function returns {bag pand id (16 digits): group key}. Layers are listed in
historical order; the viewer shows them in this order.

Sources are fetched by the s00_* steps; every one is open (CC0 or CC BY). Hand-written layers live in
curated.py and are checked against Wikipedia by s08_curated.py before they get here.
"""
import os
import csv
import json
import re
from functools import cache

import geopandas as gpd
import pandas as pd
import shapely
from shapely.geometry import Point
from pyproj import Transformer

LAYERS = []
RAW = "data/raw/layers"


def layer(**meta):
    def wrap(fn):
        LAYERS.append(dict(meta, source_fn=fn))
        return fn
    return wrap


# ---------- shared lookups ----------

@cache
def buildings() -> gpd.GeoDataFrame:
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "year", "geometry"])
    b["bag"] = b.identificatie.str.slice(-16)
    return b


@cache
def monuments() -> list[dict]:
    return json.load(open(f"{RAW}/monuments.json"))


@cache
def wikidata_panden() -> dict[str, set[str]]:
    out = {}
    for r in csv.DictReader(open("data/raw/wd_monuments.csv")):
        if r["bag"]:
            out.setdefault(r["nr"], set()).add(r["bag"].zfill(16))
    return out


def panden_of(nr) -> set[str]:
    """Buildings of a monument: the city register's links, else Wikidata's."""
    nr = str(nr)
    own = {p for m in monuments() if str(m["nr"]) == nr for p in m["panden"]}
    return own or wikidata_panden().get(nr, set())


@cache
def monument_panden() -> dict[str, set[str]]:
    out = {}
    for m in monuments():
        out.setdefault(str(m["nr"]), set()).update(m["panden"])
    for nr, ps in wikidata_panden().items():
        if not out.get(nr):
            out[nr] = set(ps)
    return out


@cache
def rce_texts() -> dict[str, str]:
    return {r["nr"]: r["txt"] for r in csv.DictReader(open("data/raw/rce_descriptions.csv"))}


def by_monument(keyed: dict[str, str]) -> dict[str, str]:
    """{monument nr: group} → {pand: group}."""
    mp = monument_panden()
    return {p: g for nr, g in keyed.items() for p in mp.get(str(nr), ())}


def within(polygons: gpd.GeoDataFrame, key_col: str) -> dict[str, str]:
    """Buildings whose centroid falls inside a polygon, keyed by the polygon's group."""
    b = buildings()
    pts = gpd.GeoDataFrame({"bag": b.bag}, geometry=b.geometry.centroid, crs=28992)
    j = gpd.sjoin(pts, polygons[[key_col, "geometry"]], predicate="within")
    return dict(zip(j.bag, j[key_col]))


def near_points(points: gpd.GeoDataFrame, key_col: str, radius: float) -> dict[str, str]:
    """Buildings within `radius` metres of a point (the building at or around an address)."""
    b = buildings()
    j = gpd.sjoin(b[["bag", "geometry"]], points[[key_col, "geometry"]].set_geometry(points.buffer(radius)),
                  predicate="intersects")
    return dict(zip(j.bag, j[key_col]))


def rd(geom_json) -> shapely.Geometry:
    return shapely.geometry.shape(geom_json if isinstance(geom_json, dict) else json.loads(geom_json))


TO_RD = Transformer.from_crs(4326, 28992, always_xy=True)


# ---------- layers ----------

@layer(
    id="heritage", section="Architecture", title="Protected heritage", era="All periods",
    text=("Delft has some 700 national monuments, most of them in the old town inside the canals."),
    source=("Rijksdienst voor het Cultureel Erfgoed, monument register", "https://monumentenregister.cultureelerfgoed.nl"),
    groups=[("Rijksmonument", "National monument")],
)
def heritage():
    return {p: "Rijksmonument" for m in monuments() for p in m["panden"]}


def _curated_layer(L):
    groups = L.get("groups") or [(L["id"], L["title"])]

    def fn():
        out = {}
        for e in L["entries"]:
            out.setdefault(e["bag"], []).append((e["group"], {"story": e["story"], "source": e["source"], "name": e["name"]}))
        return out

    LAYERS.append(dict(id=L["id"], section=L.get("section", "Discover"), title=L["title"], era=L["era"], text=L["intro"],
                       caveat=L.get("caveat"), source=("Wikipedia, per building", "https://www.wikipedia.org"),
                       groups=[tuple(g) for g in groups], source_fn=fn))


if os.path.exists("data/curated.json"):
    for _L in json.load(open("data/curated.json")):
        _curated_layer(_L)


def _residents():
    out = {}
    for r in json.load(open("data/residents.json")):
        n = out.setdefault(r["bag"], ("res", {"name": r["person"], "people": []}))[1]
        n["people"].append({k: r[k] for k in ("person", "born", "died", "desc", "quote", "url", "links", "address")})
    return out


if os.path.exists("data/residents.json"):
    LAYERS.append(dict(
        id="residents", section="Discover", title="Who lived here", era="1500–today",
        text=("Painters, scientists and writers whose Wikipedia biography names the Delft address where they lived "
              "or worked. Pick a name to fly to the house."),
        caveat=("Found automatically in Dutch Wikipedia and matched to today's address; house numbers have sometimes "
                "changed, and some houses were rebuilt since."),
        source=("Dutch Wikipedia, via Wikidata", "https://nl.wikipedia.org"),
        groups=[("res", "Home of a well-known resident")], source_fn=_residents))
