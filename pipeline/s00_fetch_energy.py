"""Energy labels per building (RVO via RIVM Atlas Leefomgeving, public domain), Amsterdam panden only."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from .city import GEMEENTE_CODE

WFS = "https://data.rivm.nl/geo/nl/wfs"
PAGE = 10000


def page(start):
    r = requests.get(WFS, timeout=300, params={
        "service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeNames": "nl:rvo_energielabels",
        "outputFormat": "application/json", "propertyName": "identificatie,dominant_label,aant_labels",
        "CQL_FILTER": f"identificatie LIKE '{GEMEENTE_CODE}%'", "sortBy": "identificatie", "count": PAGE, "startIndex": start})
    return [f["properties"] for f in r.json()["features"]]


def main():
    first = requests.get(WFS, timeout=300, params={
        "service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeNames": "nl:rvo_energielabels",
        "resultType": "hits", "CQL_FILTER": f"identificatie LIKE '{GEMEENTE_CODE}%'"}).text
    total = int(first.split('numberMatched="')[1].split('"')[0])
    with ThreadPoolExecutor(4) as ex:
        rows = [r for p in ex.map(page, range(0, total, PAGE)) for r in p]
    Path("data/raw/energy.json").write_text(json.dumps({r["identificatie"]: r["dominant_label"] for r in rows}))
    print(total, "matched;", len(rows), "fetched")


if __name__ == "__main__":
    main()
