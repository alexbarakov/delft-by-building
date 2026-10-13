"""Every address in the municipality with its building (BAG verblijfsobjecten via PDOK WFS, CC0).

Links the RCE register, which names verblijfsobjecten, to panden; also serves as a local geocoder."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from .city import BOUNDS, GEMEENTE_CODE, UA

WFS = "https://service.pdok.nl/lv/bag/wfs/v2_0"
CELL = 1000
PAGE = 1000
KEEP = ("identificatie", "openbare_ruimte", "huisnummer", "huisletter", "toevoeging", "postcode",
        "gebruiksdoel", "pandidentificatie")


def cell(x, y):
    out, start = [], 0
    while True:
        r = requests.get(WFS, params={"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                         "typeName": "bag:verblijfsobject", "outputFormat": "application/json", "count": PAGE,
                         "startIndex": start, "bbox": f"{x},{y},{x + CELL},{y + CELL}"}, headers=UA, timeout=120)
        r.raise_for_status()
        fs = r.json()["features"]
        out += [{k: f["properties"].get(k) for k in KEEP} | {"xy": f["geometry"]["coordinates"][:2]}
                for f in fs if f["properties"]["identificatie"].startswith(GEMEENTE_CODE)]
        if len(fs) < PAGE:
            return out
        start += PAGE


def main():
    cells = [(x, y) for x in range(BOUNDS[0], BOUNDS[2], CELL) for y in range(BOUNDS[1], BOUNDS[3], CELL)]
    with ThreadPoolExecutor(6) as ex:
        parts = list(ex.map(lambda c: cell(*c), cells))
    seen, rows = set(), []
    for r in (r for p in parts for r in p):
        if r["identificatie"] not in seen:
            seen.add(r["identificatie"]); rows.append(r)
    Path("data/raw/addresses.json").write_text(json.dumps(rows, ensure_ascii=False))
    print(len(rows), "addresses")


if __name__ == "__main__":
    main()
