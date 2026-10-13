"""Verify the curated entries against their Wikipedia articles and geocode them to BAG buildings."""
import csv
import json
import re
from functools import cache
from urllib.parse import quote

import geopandas as gpd
import requests
from shapely.geometry import Point

from .curated import CURATED
from .geo import lookup

from .city import UA, WOONPLAATS


@cache
def article(ref):
    lang, title = ref.split(":", 1)
    r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", headers=UA, timeout=60, params={
        "action": "query", "prop": "extracts|info", "inprop": "url", "explaintext": 1, "redirects": 1,
        "format": "json", "titles": title}).json()
    page = next(iter(r["query"]["pages"].values()))
    return (page.get("extract") or ""), page.get("fullurl")


@cache
def buildings():
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "geometry"])
    b["bag"] = b.identificatie.str.slice(-16)
    return b


def geocode(address):
    hit = lookup(address)
    return (hit[0], hit[2]) if hit else (None, None)


@cache
def wikidata_bags():
    """Wikipedia article URL → BAG ids of the building it is about, as s06_wiki placed its Wikidata item."""
    out = {}
    for it in json.load(open("data/wd_places.json")).values():
        for url in (it["en"], it["nl"]):
            if url:
                out.setdefault(url, set()).update(it["bags"])
    return out


def main():
    out, dropped = [], []
    for L in CURATED:
        entries = []
        for name, address, story, ref, checks, *group in L["entries"]:
            text, url = article(ref)
            missing = [c for c in checks if c not in text]
            # An article about the building itself names its BAG ids in Wikidata: trust those over the
            # geocoder, which can land on a neighbouring part of a large complex (the Palace, the Scheepvaarthuis).
            own = wikidata_bags().get(url)
            # ... unless the item stands for a whole complex (a garden village of 170 houses): then the address decides.
            own = own if own and len(own) <= 20 else None
            bags, found = (sorted(own), "wikidata") if own else ((lambda b, f: ([b] if b else [], f))(*geocode(address)))
            if missing or not bags:
                dropped.append((L["id"], name, missing, found))
                continue
            for bag in bags:
                entries.append(dict(name=name, address=address, bag=bag, story=story, source=url,
                                    group=group[0] if group else L["id"]))
        out.append(dict({k: v for k, v in L.items() if k != "entries"}, entries=entries))
        print(f'{L["id"]:10s} {len(entries)}/{len(L["entries"])}')
    for d in dropped:
        print("dropped:", d)
    json.dump(out, open("data/curated.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
