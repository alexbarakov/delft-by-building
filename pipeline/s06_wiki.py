"""Names, photos and article extracts for buildings that have a Wikidata item.

An item lands on its BAG id (P5208), else on the panden of its monument number (P359), else on the pand
its coordinates fall in.

wiki.json: list of {label, wiki: {lang, url, extract} | null, architects, styles, image: {thumb, page,
artist, license, licenseUrl} | null}. data/wiki_index.parquet maps each pand to its entry.
Photos are Wikimedia Commons files with their author and licence, as the Commons API reports them.
"""
import csv
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import requests

from .city import UA


def get_json(url, params):
    """GET with backoff: the Wikimedia APIs answer bursts with 429 and an HTML page."""
    for attempt in range(6):
        r = requests.get(url, params=params, headers=UA, timeout=60)
        if r.ok and r.headers.get("content-type", "").startswith("application/json"):
            time.sleep(0.3)
            return r.json()
        time.sleep(2 ** attempt)
    r.raise_for_status()
    raise RuntimeError(f"{url}: {r.status_code} {r.text[:200]}")


def batched(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def extracts(lang, titles):
    out = {}
    for chunk in batched(sorted(titles), 20):
        r = get_json(f"https://{lang}.wikipedia.org/w/api.php", {
            "action": "query", "format": "json", "prop": "extracts", "exintro": 1, "explaintext": 1,
            "exsentences": 3, "exlimit": 20, "redirects": 1, "titles": "|".join(chunk)})
        norm = {n["to"]: n["from"] for n in r["query"].get("normalized", []) + r["query"].get("redirects", [])}
        for p in r["query"]["pages"].values():
            t = p.get("title")
            while t in norm:
                t = norm[t]
            if p.get("extract"):
                out[t] = p["extract"].strip()
    return out


def strip_html(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or ""))).strip()


def artist_of(meta):
    a = strip_html(meta.get("Artist", {}).get("value"))[:80]
    if not a or re.match(r"^\d{1,2}:\d{2}|^\d{1,2} \w+ \d{4}|^\d{4}-\d{2}-\d{2}|^unknown", a, re.I):
        return None
    return a


def images(files):
    out = {}
    for chunk in batched(sorted(files), 50):
        r = get_json("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata",
            "iiurlwidth": 500, "titles": "|".join("File:" + f for f in chunk)})
        norm = {n["to"]: n["from"] for n in r["query"].get("normalized", [])}
        for p in r["query"]["pages"].values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                continue
            m = ii.get("extmetadata", {})
            key = norm.get(p["title"], p["title"])[5:]
            out[key] = dict(thumb=ii.get("thumburl"), page=ii.get("descriptionurl"),
                            artist=artist_of(m),
                            license=m.get("LicenseShortName", {}).get("value"),
                            licenseUrl=m.get("LicenseUrl", {}).get("value"))
    return out


def title_of(url):
    return unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")


def place(rows):
    """Wikidata item → set of panden."""
    import geopandas as gpd
    from shapely.geometry import Point
    mon = {str(m["nr"]): set(m["panden"]) for m in json.load(open("data/raw/layers/monuments.json"))}
    p = gpd.read_parquet("data/panden.parquet", columns=["identificatie", "geometry"])
    bags, sidx = p.identificatie.str.slice(-16).to_numpy(), p.sindex
    to_rd = __import__("pyproj").Transformer.from_crs(4326, 28992, always_xy=True)
    out = {}
    for r in rows:
        if r["bag"]:
            out[r["i"]] = {r["bag"].zfill(16)}
        elif mon.get(r["nr"]):
            out[r["i"]] = mon[r["nr"]]
        elif r["coord"].startswith("Point("):
            lon, lat = map(float, r["coord"][6:-1].split())
            pt = Point(to_rd.transform(lon, lat))
            hit = sidx.query(pt, predicate="within")
            if len(hit):
                out[r["i"]] = {bags[hit[0]]}
    return out


def main():
    rows = list(csv.DictReader(open("data/raw/wd_buildings.csv")))
    where = place(rows)
    first = {r["i"]: r for r in rows}
    Path("data/wd_places.json").write_text(json.dumps({i: dict(bags=sorted(b), en=first[i]["en"], nl=first[i]["nl"])
                                                       for i, b in where.items()}, ensure_ascii=False))
    items = {}
    for r in rows:
        if r["i"] not in where:
            continue
        it = items.setdefault(r["i"], dict(bags=set(), label=r["labelEn"] or r["labelNl"], label_nl=r["labelNl"] or r["labelEn"],
                                           en=r["en"], nl=r["nl"],
                                           image=None, architects=[a for a in r["architects"].split("|") if a],
                                           styles=[s for s in r["styles"].split("|") if s]))
        it["bags"] |= where[r["i"]]
        if r["image"] and not it["image"]:
            it["image"] = unquote(r["image"].rsplit("/", 1)[1]).replace("_", " ")

    ex_en = extracts("en", {title_of(i["en"]) for i in items.values() if i["en"]})
    ex_nl = extracts("nl", {title_of(i["nl"]) for i in items.values() if i["nl"]})
    imgs = images({i["image"] for i in items.values() if i["image"]})
    print(f"extracts en {len(ex_en)}, nl {len(ex_nl)}; images {len(imgs)}")

    entries, index = [], {}
    # Rank: an article first, then a photo, so a pand with two items shows the richer one.
    for it in sorted(items.values(), key=lambda i: (not (i["en"] or i["nl"]), not i["image"])):
        wiki = None
        if it["en"]:
            wiki = dict(lang="en", url=it["en"], extract=ex_en.get(title_of(it["en"])))
        elif it["nl"]:
            wiki = dict(lang="nl", url=it["nl"], extract=ex_nl.get(title_of(it["nl"])))
        img = imgs.get(it["image"]) if it["image"] else None
        if not (wiki or img):
            continue
        k = len(entries)
        wiki_nl = dict(lang="nl", url=it["nl"], extract=ex_nl.get(title_of(it["nl"]))) if it["nl"] else None
        entries.append(dict(label=it["label"], label_nl=it["label_nl"], wiki=wiki, wiki_nl=wiki_nl,
                            architects=it["architects"], styles=it["styles"], image=img))
        for b in it["bags"]:
            index.setdefault(b, k)
    # Photos found on Commons by address (s10_commons) fill buildings that have none yet.
    commons = Path("data/commons_best.json")
    if commons.exists():
        best = json.loads(commons.read_text())
        need = {bag: f for bag, f in best.items()
                if bag not in index or not entries[index[bag]].get("image")}
        found = images({f["title"][5:] for f in need.values()})
        added = 0
        for bag, f in need.items():
            img = found.get(f["title"][5:])
            if not img or not img.get("thumb"):
                continue
            if bag in index:
                entries[index[bag]]["image"] = img
            else:
                index[bag] = len(entries)
                entries.append(dict(label=None, label_nl=None, wiki=None, wiki_nl=None, architects=[], styles=[], image=img))
            added += 1
        print(added, "buildings got a Commons photo by address")
    Path("web/data/wiki.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")))
    pd.DataFrame({"bag": list(index), "wk": list(index.values())}).to_parquet("data/wiki_index.parquet")
    print(len(entries), "entries for", len(index), "panden;", Path("web/data/wiki.json").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
