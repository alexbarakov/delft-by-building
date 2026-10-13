"""Fetch the open sources behind the history layers into data/raw/layers/.

Amsterdam city API (CC0 / CC-BY), maps.amsterdam.nl open geodata, RCE linked data (CC0).
Not fetched: the Joods Monument graph of the Amsterdam Time Machine, which has no licence
and asks not to be used without permission.
"""
import json
from pathlib import Path

import requests

OUT = Path("data/raw/layers")
API = "https://api.data.amsterdam.nl/v1"
from .city import UA


def paged(url, key, params=None):
    items, params = [], {"_format": "json", "_pageSize": 1000, **(params or {})}
    while url:
        d = requests.get(url, params=params, headers=UA, timeout=120).json()
        items += d["_embedded"][key]
        url = d.get("_links", {}).get("next", {}).get("href")
        params = None
    return items


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False))
    print(name, len(data) if isinstance(data, list) else len(data.get("features", [])))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mons = paged(f"{API}/monumenten/monumenten/", "monumenten")
    save("monuments.json", [dict(
        nr=m["monumentnummer"], status=m["status"], type=m["type"], name=m["naam"], address=m["adressering"],
        architect=m["architectOntwerp"], function=m["oorspronkelijkeFunctie"],
        panden=[p["identificatie"] for p in m["_links"].get("betreftBagPand") or []]) for m in mons])

    save("ww2_damage.geojson", requests.get("https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php",
         params={"KAARTLAAG": "WOII", "THEMA": "woii"}, headers=UA, timeout=120).json())
    save("ww2_impacts.json", paged(f"{API}/ontplofbare_oorlogsresten/inslagen/", "inslagen"))
    save("unesco.json", paged(f"{API}/monumenten/unesco/", "unesco"))
    save("stadsgezichten.json", paged(f"{API}/beschermdestadsdorpsgezichten/beschermdestadsdorpsgezichten/",
                                      "beschermdestadsdorpsgezichten"))
    save("social_housing.geojson", requests.get("https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php",
         params={"KAARTLAAG": "AFWC_2025", "THEMA": "afwc_2025"}, headers=UA, timeout=300).json())

    q = """PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
    SELECT ?nr ?style WHERE { ?m ceo:heeftBasisregistratieRelatie/ceo:gemeentenaam "Amsterdam" ;
      ceo:rijksmonumentnummer ?nr ; ceo:heeftStijlEnCultuur/ceo:heeftStijlEnCultuurNaam/<http://www.w3.org/2004/02/skos/core#prefLabel> ?style }"""
    r = requests.post("https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
                      data={"query": q}, headers={"Accept": "application/sparql-results+json", **UA}, timeout=120)
    save("rce_styles.json", [{"nr": b["nr"]["value"], "style": b["style"]["value"]} for b in r.json()["results"]["bindings"]])


if __name__ == "__main__":
    main()
