"""Link every rijksmonument to its BAG buildings: through the addresses RCE registers (verblijfsobject →
pand), else through the monument's own outline (panden covered for at least half their footprint)
or point (the pand it falls in). Bridges and other points in the open stay unlinked.
Writes data/raw/layers/monuments.json, the shape every layer reads."""
import csv
import json
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import shapely
import shapely.geometry

RAW = Path("data/raw")


def main():
    addr = {a["identificatie"]: a for a in json.load(open(RAW / "addresses.json"))}
    p = gpd.read_parquet("data/panden.parquet", columns=["identificatie", "geometry"])
    p["bag"] = p.identificatie.str.slice(-16)
    p["geometry"] = shapely.make_valid(p.geometry.values)
    known = set(p.bag)
    by_vbo, addresses = defaultdict(set), defaultdict(list)
    for r in csv.DictReader(open(RAW / "rce_bag.csv")):
        a = addr.get(r["vbo"])
        if a and a["pandidentificatie"] in known:
            by_vbo[r["nr"]].add(a["pandidentificatie"])
            addresses[r["nr"]].append(f'{a["openbare_ruimte"]} {a["huisnummer"]}{a["huisletter"] or ""}')
    by_geom = {}
    sidx = p.sindex
    for r in csv.DictReader(open(RAW / "rce_geom.csv")):
        if r["nr"] in by_vbo or not r["wkt"]:
            continue
        g = shapely.from_wkt(r["wkt"].strip('"'))
        if g.geom_type == "Point":   # a point counts for the building it stands in, or one within 3 m
            hits = p.iloc[sidx.query(g.buffer(3), predicate="intersects")]
            ps = set(hits.bag[hits.contains(g)]) or set(hits.bag[:1])
        else:
            hits = p.iloc[sidx.query(g, predicate="intersects")]
            share = hits.geometry.intersection(g).area / hits.geometry.area
            ps = set(hits.bag[share >= 0.5])
        if ps:
            by_geom[r["nr"]] = ps
    # The city's own monument map (Gemeente Delft, CC BY 4.0): an outline per monument, national and municipal.
    city, municipal = {}, {}
    for ft in json.load(open(RAW / "layers/delft_monuments.geojson"))["features"]:
        pr, g = ft["properties"], shapely.geometry.shape(ft["geometry"]) if ft["geometry"] else None
        if g is None or pr.get("BRUG") == "ja":
            continue
        g = shapely.make_valid(g)
        hits = p.iloc[sidx.query(g, predicate="intersects")]
        share = hits.geometry.intersection(g).area / hits.geometry.area
        ps = set(hits.bag[share >= 0.5])
        if not ps:
            continue
        if pr["TYPE"] == "Rijks" and pr.get("NUMMER", "").strip().isdigit():
            city.setdefault(pr["NUMMER"].strip(), set()).update(ps)
        elif pr["TYPE"] == "Gemeente":
            municipal[pr["MON_ID"]] = (pr["OBJECTNAAM"].strip(), ps)
    names = {r["nr"]: r["label"] for r in csv.DictReader(open(RAW / "wd_monuments.csv")) if r["label"]}
    arch = defaultdict(set)
    for r in csv.DictReader(open(RAW / "wd_monuments.csv")):
        if r["architectLabel"] and not r["architectLabel"].startswith("http"):
            arch[r["nr"]].add(r["architectLabel"])
    func = defaultdict(list)
    for r in csv.DictReader(open(RAW / "rce_functions.csv")):
        func[r["nr"]].append(r["function"])
    nrs = sorted(set(by_vbo) | set(by_geom) | set(city), key=int)
    out = [dict(nr=int(nr), status="Rijksmonument", type="Rijksmonument", name=names.get(nr, ""),
                address=sorted(set(addresses[nr]))[0] if addresses[nr] else "",
                architect=", ".join(sorted(arch[nr])), function=", ".join(func[nr]),
                panden=sorted(by_vbo.get(nr, set()) | city.get(nr, set()) or by_geom.get(nr, set()))) for nr in nrs]
    out += [dict(nr=f"g{k}", status="Gemeentelijk monument", type="Gemeentelijk monument", name="", address=name,
                 architect="", function="", panden=sorted(ps)) for k, (name, ps) in municipal.items()]
    (RAW / "layers").mkdir(exist_ok=True)
    (RAW / "layers/monuments.json").write_text(json.dumps(out, ensure_ascii=False))
    total = len({r["nr"] for r in csv.DictReader(open(RAW / "rce_geom.csv"))})
    print(f"{len(nrs)} of {total} national monuments linked: {len(by_vbo)} by address, {len(city)} by the city's outlines, "
          f"{len(by_geom)} by RCE outline; {len(municipal)} municipal monuments; "
          f"{len({b for m in out for b in m['panden']})} panden")


if __name__ == "__main__":
    main()
