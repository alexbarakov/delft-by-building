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

RAW = Path("data/raw")


def main():
    addr = {a["identificatie"]: a for a in json.load(open(RAW / "addresses.json"))}
    p = gpd.read_parquet("data/panden.parquet", columns=["identificatie", "geometry"])
    p["bag"] = p.identificatie.str.slice(-16)
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
    names = {r["nr"]: r["label"] for r in csv.DictReader(open(RAW / "wd_monuments.csv")) if r["label"]}
    arch = defaultdict(set)
    for r in csv.DictReader(open(RAW / "wd_monuments.csv")):
        if r["architectLabel"] and not r["architectLabel"].startswith("http"):
            arch[r["nr"]].add(r["architectLabel"])
    func = defaultdict(list)
    for r in csv.DictReader(open(RAW / "rce_functions.csv")):
        func[r["nr"]].append(r["function"])
    nrs = sorted(set(by_vbo) | set(by_geom), key=int)
    out = [dict(nr=int(nr), status="Rijksmonument", type="Rijksmonument", name=names.get(nr, ""),
                address=sorted(set(addresses[nr]))[0] if addresses[nr] else "",
                architect=", ".join(sorted(arch[nr])), function=", ".join(func[nr]),
                panden=sorted(by_vbo.get(nr) or by_geom[nr])) for nr in nrs]
    (RAW / "layers").mkdir(exist_ok=True)
    (RAW / "layers/monuments.json").write_text(json.dumps(out, ensure_ascii=False))
    total = len({r["nr"] for r in csv.DictReader(open(RAW / "rce_geom.csv"))})
    print(f"{len(out)} of {total} monuments linked: {len(by_vbo)} by address, {len(by_geom)} by outline; "
          f"{len({b for m in out for b in m['panden']})} panden")


if __name__ == "__main__":
    main()
