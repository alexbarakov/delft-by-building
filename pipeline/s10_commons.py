"""More photos from Wikimedia Commons: geotagged files whose title names the address or the monument number.

1. Walk the built-up city in 250 m cells with the Commons geosearch (cells that hit the 500 limit split in four).
2. Read each title: 'Herengracht 276.JPG', 'Keizersgracht 272tm284', 'met RM2558tm65' → addresses or monuments.
3. Addresses are geocoded to BAG buildings (PDOK Locatieserver, local BAG addresses, exact number); a match counts only
   when the photo was taken within 150 m of the building, which rules out same-named streets elsewhere.
4. Per building the best photo wins: a title naming this one address over a row, a recent photo over an archive one.
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import requests
from pyproj import Transformer
from shapely.geometry import Point

from .city import UA
from .geo import lookup, streets as all_streets
API = "https://commons.wikimedia.org/w/api.php"
CACHE = Path("data/raw/commons_geo.json")
TO_RD = Transformer.from_crs(4326, 28992, always_xy=True)
TO_LL = Transformer.from_crs(28992, 4326, always_xy=True)


def get(params):
    for attempt in range(6):
        try:
            r = requests.get(API, params=dict(params, format="json"), headers=UA, timeout=60)
            if r.ok and r.headers.get("content-type", "").startswith("application/json"):
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 ** attempt)
    return {}


def cell(box, depth=0):
    """Geotagged files in a lat/lon box; split the box when the search hits its limit."""
    s, w, n, e = box
    d = get({"action": "query", "list": "geosearch", "gsnamespace": 6, "gslimit": 500, "gsbbox": f"{n}|{w}|{s}|{e}"})
    hits = d.get("query", {}).get("geosearch", [])
    if len(hits) >= 500 and depth < 4:
        ms, mw = (s + n) / 2, (w + e) / 2
        return [h for b in [(s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)] for h in cell(b, depth + 1)]
    return [dict(title=h["title"], lat=h["lat"], lon=h["lon"]) for h in hits]


def harvest(buildings):
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    x0, y0, x1, y1 = buildings.total_bounds
    cells = []
    for x in np.arange(x0, x1, 250):
        for y in np.arange(y0, y1, 250):
            cells.append((x, y))
    sidx = buildings.sindex
    cells = [(x, y) for x, y in cells if len(sidx.query(gpd.points_from_xy([x + 125], [y + 125]).buffer(125)[0])) > 0]
    boxes = []
    for x, y in cells:
        w, s = TO_LL.transform(x, y)
        e, n = TO_LL.transform(x + 250, y + 250)
        boxes.append((s, w, n, e))
    print(len(boxes), "cells")
    with ThreadPoolExecutor(4) as ex:
        files = [f for fs in ex.map(cell, boxes) for f in fs]
    files = list({f["title"]: f for f in files}.values())
    CACHE.write_text(json.dumps(files, ensure_ascii=False))
    return files


def numbers(spec):
    """'272' → [272]; '272tm284' or '272-284' → the even or odd numbers between; '281 283' → both."""
    m = re.match(r"(\d+)\s*(?:tm|t/m|-|–)\s*(\d+)$", spec)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 0 < b - a <= 24:
            return list(range(a, b + 1, 2))
    return [int(n) for n in re.findall(r"\d+", spec)][:4]


GEO = {}


def geocode(address):
    hit = lookup(address)
    GEO[address] = hit[1] if hit else None
    return GEO[address]


def main():
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "geometry"])
    b["bag"] = b.identificatie.str.slice(-16)
    files = harvest(b)
    print(len(files), "geotagged files")

    streets = [s for s in all_streets() if len(s) > 3]
    addr_re = re.compile(r"(?<![A-Za-z])(" + "|".join(map(re.escape, streets)) +
                         r")[ _,]+(\d{1,4}(?:\s*(?:tm|t/m|-|–)\s*\d{1,4}|(?:\s+\d{1,4})*)?)(?![\d])")
    rm_re = re.compile(r"\bRM\s?(\d{3,6})(?:\s*tm\s*(\d{1,6}))?|rijksmonument[ _-]?(\d{3,6})", re.I)
    monuments = json.load(open("data/raw/layers/monuments.json"))
    mon_panden = {}
    for m in monuments:
        mon_panden.setdefault(str(m["nr"]), set()).update(m["panden"])

    candidates = []  # (bag, score, file)
    jobs = []
    for f in files:
        title = f["title"][5:].rsplit(".", 1)[0].replace("_", " ")
        archive = bool(re.search(r"Bestanddeelnr|Collectie|panoramio|\(\d{6,}\)", title))
        for m in rm_re.finditer(title):
            a = m.group(1) or m.group(3)
            nrs = [a]
            if m.group(2):  # 'RM2558tm65' runs from 2558 to 2565: the end borrows the start's leading digits
                g = m.group(2)
                end = int(a[:len(a) - len(g)] + g) if len(g) < len(a) else int(g)
                if 0 < end - int(a) <= 12:
                    nrs = [str(n) for n in range(int(a), end + 1)]
            for nr in nrs:
                for p in mon_panden.get(nr, ()):
                    candidates.append((p, 2 - archive, f))
        for m in addr_re.finditer(title):
            nums = numbers(m.group(2))
            for n in nums:
                jobs.append((f"{m.group(1)} {n}", f, (3 if len(nums) == 1 else 1) - archive))

    # Municipal monuments: Wiki Loves Monuments files carry {{Gemeentelijk monument|0503/<id>}} (harvested to
    # data/raw/commons_gm.json); a street view of the house beats an interior.
    gm = Path("data/raw/commons_gm.json")
    if gm.exists():
        for mid, titles in json.loads(gm.read_text()).items():
            for t in sorted(titles, key=lambda t: bool(re.search(r"interieur|interior|detail", t, re.I))):
                for p in mon_panden.get(f"g{mid}", ()):
                    candidates.append((p, 2 if not re.search(r"interieur|interior|detail", t, re.I) else 0, {"title": t}))
                break
    print(len(jobs), "address mentions")
    uniq = sorted({a for a, _, _ in jobs})
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(geocode, uniq))
    sidx = b.sindex
    for address, f, score in jobs:
        pt = GEO.get(address)
        if not pt:
            continue
        x, y = TO_RD.transform(f["lon"], f["lat"])
        if (x - pt[0]) ** 2 + (y - pt[1]) ** 2 > 150 ** 2:
            continue
        hit = b.iloc[sidx.query(Point(pt), predicate="intersects")]
        for p in hit.bag:
            candidates.append((p, score, f))

    best = {}
    for p, score, f in candidates:
        if p not in best or score > best[p][0]:
            best[p] = (score, f)
    print(len(best), "buildings with a Commons photo")
    Path("data/commons_best.json").write_text(json.dumps({p: dict(score=s, **f) for p, (s, f) in best.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
