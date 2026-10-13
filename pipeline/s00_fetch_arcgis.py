"""Fetch layers of the City of Delft's open data portal (ArcGIS Online, data.delft.nl) as GeoJSON in RD New.

Monumenten: national and municipal monuments. gebouwen_1832 / percelen_1832: the first cadastre (1832), its
buildings and plots. Welstand_Cultuurhistorisch_waardevolle_panden: buildings the city counts as valuable."""
import json
import sys
from pathlib import Path

import requests

from .city import UA

ROOT = "https://services3.arcgis.com/j07voPd56xoB4c87/ArcGIS/rest/services"
SERVICES = {"Monumenten_test": "delft_monuments", "gebouwen_1832": "gebouwen_1832", "percelen_1832": "percelen_1832",
            "water_1832": "water_1832", "Welstand_Cultuurhistorisch_waardevolle_panden": "waardevolle_panden"}


def fetch(service):
    meta = requests.get(f"{ROOT}/{service}/FeatureServer", params={"f": "json"}, headers=UA, timeout=60).json()
    layer = meta["layers"][0]["id"]
    feats, off = [], 0
    while True:
        d = requests.get(f"{ROOT}/{service}/FeatureServer/{layer}/query", headers=UA, timeout=300, params={
            "where": "1=1", "outFields": "*", "f": "geojson", "outSR": 28992,
            "resultOffset": off, "resultRecordCount": 1000}).json()
        fs = d.get("features", [])
        feats += fs
        off += len(fs)
        if len(fs) < 1000:
            return feats


def main():
    out = Path("data/raw/layers")
    out.mkdir(parents=True, exist_ok=True)
    for service, name in SERVICES.items():
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        feats = fetch(service)
        (out / f"{name}.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
        print(name, len(feats), sorted(feats[0]["properties"]) if feats else "")


if __name__ == "__main__":
    main()
