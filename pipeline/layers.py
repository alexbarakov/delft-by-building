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
import numpy as np
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

@cache
def rce_functions() -> dict[str, set[str]]:
    out = {}
    for r in csv.DictReader(open("data/raw/rce_functions.csv")):
        out.setdefault(r["nr"], set()).add(re.sub(r"\s*\(.*$", "", r["function"]).strip())
    return out


@layer(
    id="gables", section="Architecture", title="Gables", era="1400–1900",
    text=("Most listed houses in Delft face the street with a flat cornice, many of them put up in the 1700s and "
          "1800s. The older tops are rarer: pointed and spout gables from the wooden-house tradition, stepped gables "
          "of the 1500s and 1600s, and a handful of bell gables."),
    caveat="Listed houses only: the register of national monuments names the gable of each.",
    source=("Rijksmonumentenregister, RCE", "https://monumentenregister.cultureelerfgoed.nl"),
    groups=[("trap", "Stepped gable"), ("punt", "Pointed or spout gable"), ("klok", "Bell or neck gable"),
            ("lijst", "Cornice")],
)
def gables():
    pats = [("trap", r"trapgevel"), ("punt", r"puntgevel|tuitgevel"), ("klok", r"klokgevel|halsgevel"),
            ("lijst", r"rechte lijst|lijstgevel|verhoogde lijst")]
    keyed = {}
    for nr, t in rce_texts().items():
        t = t.lower()
        hits = [(m.start(), k) for k, p in pats for m in [re.search(p, t)] if m]
        if hits:
            keyed[nr] = min(hits)[1]  # the first gable named is the house's own
    return by_monument(keyed)


@layer(
    id="heritage", section="Architecture", title="Protected heritage", era="All periods",
    text=("Listed buildings, by the State for national significance or by the city for local value, and some 1,500 "
          "more that the city's design rules count as worth keeping. Most stand in the old town inside the canals."),
    source=("Gemeente Delft, monuments", "https://data.delft.nl/datasets/monumenten-1"),
    groups=[("Rijksmonument", "National monument"), ("Gemeentelijk monument", "Municipal monument"),
            ("waardevol", "Valued by the city, not listed")],
)
def heritage():
    out = {}
    for m in monuments():
        for p in m["panden"]:
            if m["status"] == "Rijksmonument" or p not in out:
                out[p] = m["status"]
    # Buildings the city's design rules count as of cultural-historical value (Welstand), unlisted
    v = gpd.read_file(f"{RAW}/waardevolle_panden.geojson").set_crs(28992, allow_override=True)
    b = buildings()
    j = gpd.sjoin(gpd.GeoDataFrame({"bag": b.bag}, geometry=b.geometry.representative_point(), crs=28992),
                  v[["geometry"]], predicate="within")
    for p in j.bag:
        out.setdefault(p, "waardevol")
    return out


def _curated_layer(L):
    groups = L.get("groups") or [(L["id"], L["title"])]

    def fn():
        out = {}
        for e in L["entries"]:
            out.setdefault(e["bag"], []).append((e["group"], {"story": e["story"], "source": e["source"], "name": e["name"],
                                                           "address": e["address"]}))
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


# ---------- the first cadastre, 1832 ----------
# Owners and their trades from the 1832 land register (Erfgoed Delft open data, OAT Kadaster 1832), joined by parcel
# code to the city's map of the 1832 parcels; a building today belongs to the parcel its centre falls in.
TRADES = [
    ("potter", "Delftware potters", {"plateelbakker": "Delftware potter", "platheelbakker": "Delftware potter",
                                     "plateelbakkersknecht": "Delftware potter's hand"}),
    ("drink", "Inns, taverns and distillers", {"tapper": "tavern keeper", "tapster": "tavern keeper",
        "kastelein": "innkeeper", "herbergier": "innkeeper", "logementhouder": "lodging-house keeper",
        "logementhoudster": "lodging-house keeper", "slijter": "liquor seller", "brander": "distiller",
        "likeurstoker": "liqueur distiller", "azijnmaker": "vinegar maker"}),
    ("food", "Bakers, butchers and grocers", {"broodbakker": "baker", "koekbakker": "cake baker",
        "vleeshouwer": "butcher", "spekslager": "pork butcher", "grutter": "grocer", "boterkoopster": "butter seller",
        "turfverkoopster": "peat seller"}),
    ("trade", "Merchants and shopkeepers", {"koopman": "merchant", "koopvrouw": "merchant", "winkelier": "shopkeeper",
        "winkelierster": "shopkeeper", "houtkoper": "timber merchant", "ijzerkoper": "ironmonger",
        "korenkoper": "corn merchant", "tabakskoper": "tobacco merchant", "drogist": "druggist", "apotheker": "apothecary",
        "uitdrager": "second-hand dealer", "lakenfabrikant": "cloth manufacturer"}),
    ("craft", "Craftsmen", {"timmerman": "carpenter", "metselaar": "bricklayer", "smid": "smith",
        "schoenmaker": "shoemaker", "kleermaker": "tailor", "verver": "dyer", "koperslager": "coppersmith",
        "blikslager": "tinsmith", "kuiper": "cooper", "zadelmaker": "saddler", "mandenmaker": "basket maker",
        "looier": "tanner", "leerlooier": "tanner", "zeepzieder": "soap boiler", "kaarsenmaker": "candle maker",
        "bezemmaker": "broom maker", "wagenmaker": "wheelwright", "draaier": "turner", "scheepsmaker": "shipwright"}),
]
PROPERTY_EN = {"huis en erf": "house and yard", "huis": "house", "huis, schuur en erf": "house, barn and yard",
               "pakhuis": "warehouse", "pakhuis en erf": "warehouse and yard", "huis, erf en schuur": "house, yard and barn",
               "schuur": "barn", "schuur en erf": "barn and yard", "stal": "stable", "stal en erf": "stable and yard",
               "werkplaats": "workshop", "huis, gebouw en erf": "house, building and yard", "tuinhuis": "garden house"}
TRADE_OF = {nl: (key, en) for key, _, d in TRADES for nl, en in d.items()}


@cache
def cadastre_1832():
    """pand → (group, note) for buildings on a built parcel of 1832 whose owner the register names."""
    owners = {}
    for r in csv.DictReader(open("data/raw/kadaster_1832.csv", encoding="utf-8", errors="ignore"), delimiter=";"):
        kind = r["VVPA_SOORT EIGENDOM"].strip().lower()
        if kind not in PROPERTY_EN or r["PLPA_KADASTRALE GEMEENTE"] != "Delft":
            continue
        name = " ".join(x for x in (r["PPA_VOORNAAM"], r["PPA_TUSSENVOEGSEL"], r["PPA_ACHTERNAAM"]) if x.strip())
        owners.setdefault(r["AK_KOPPELVELD"], []).append((name, r["PPA_BEROEP"].strip().lower(), kind, r["AK_PID"]))
    plots = gpd.read_file(f"{RAW}/percelen_1832.geojson").set_crs(28992, allow_override=True)
    plots = plots[plots.KOPPELNR.isin(owners)]
    b = buildings()
    # Only buildings that stand where a building of 1832 stood (60% of today's footprint): a 1990s block on an
    # old plot belongs to the plot, not to the town of 1832.
    old = gpd.read_file(f"{RAW}/gebouwen_1832.geojson").set_crs(28992, allow_override=True)
    old_union = shapely.union_all(shapely.make_valid(old.geometry.values))
    geom = shapely.make_valid(b.geometry.values)
    near = shapely.intersects(geom, old_union)
    cover = np.zeros(len(b))
    cover[near] = shapely.area(shapely.intersection(geom[near], old_union)) / shapely.area(geom[near])
    # ... and that are not plainly younger: a house the map dates after 1900 is a rebuilding on the old footprint.
    b = b[(cover >= 0.6) & (b.year.to_numpy() <= 1900)]
    pts = gpd.GeoDataFrame({"bag": b.bag}, geometry=b.geometry.representative_point(), crs=28992)
    j = gpd.sjoin(pts, plots[["KOPPELNR", "SECTIELETT", "PERCNR", "geometry"]], predicate="within")
    out = {}
    for bag, code, sec, nr in zip(j.bag, j.KOPPELNR, j.SECTIELETT, j.PERCNR):
        name, trade, kind, pid = owners[code][0]
        key, trade_en = TRADE_OF.get(trade, ("other", None))
        who_en = f"{name}, {trade_en}" if trade_en else (f"{name} ({trade})" if trade else name)
        who_nl = f"{name}, {trade}" if trade else name
        more = len({o[0] for o in owners[code]}) - 1
        story = f"In the land register of 1832 parcel {sec} {nr}, {PROPERTY_EN[kind]}, belonged to {who_en}."
        story_nl = f"In het kadaster van 1832 was perceel {sec} {nr}, {kind}, van {who_nl}."
        if more:
            story += f" {more} more owner{'s' if more > 1 else ''} share{'' if more > 1 else 's'} the entry."
            story_nl += f" Nog {more} eigena{'ren' if more > 1 else 'ar'} op dezelfde regel."
        out[bag] = (key, {"story": story, "story_nl": story_nl, "source": pid})
    return out


LAYERS.append(dict(
    id="kadaster1832", section="Discover", title="Delft in 1832", era="1832",
    text=("The first national land register, drawn up in 1832, names the owner of every plot and often their trade. "
          "Each building that stands where a building of 1832 stood shows who owned it then: potters, innkeepers, "
          "bakers, merchants and craftsmen among them."),
    caveat=("Only buildings that stand on the footprint of a building of 1832 and that the map dates no later than "
            "1900; those after 1832 may be a rebuilding. Old town only, where the 1832 parcels are mapped."),
    source=("Erfgoed Delft, Kadaster 1832; Gemeente Delft, percelen 1832", "https://erfgoeddelft.nl/stadsarchief/open-data"),
    groups=[(k, label) for k, label, _ in TRADES] + [("other", "Other owners")],
    source_fn=cadastre_1832))
