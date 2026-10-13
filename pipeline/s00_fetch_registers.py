"""Fetch the registers every step builds on: the municipal boundary, the 3D BAG tile list,
RCE monument descriptions (CC0) and Wikidata items linked to BAG buildings (CC0)."""
import csv
import io
from pathlib import Path

import requests

from .city import GEMEENTE_CODE, NAME, UA, WIKIDATA

RAW = Path("data/raw")
RCE = "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql"
WD = "https://query.wikidata.org/sparql"
PFX = """PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

QUERIES = {
    "rce_descriptions.csv": (RCE, PFX + f"""SELECT ?nr (SAMPLE(?t) AS ?txt) WHERE {{ ?m ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <http://standaarden.overheid.nl/owms/terms/{NAME}_(gemeente)> ;
  ceo:rijksmonumentnummer ?nr ; ceo:heeftOmschrijving/ceo:omschrijving ?t }} GROUP BY ?nr"""),
    "rce_bag.csv": (RCE, PFX + f"""SELECT DISTINCT ?nr ?vbo WHERE {{ ?m ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <http://standaarden.overheid.nl/owms/terms/{NAME}_(gemeente)> ;
  ceo:rijksmonumentnummer ?nr ; ceo:heeftBasisregistratieRelatie/ceo:heeftBAGRelatie/ceo:verblijfsobjectIdentificatie ?vbo }}"""),
    "rce_geom.csv": (RCE, PFX + f"""SELECT ?nr (SAMPLE(?w) AS ?wkt) WHERE {{ ?m ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <http://standaarden.overheid.nl/owms/terms/{NAME}_(gemeente)> ;
  ceo:rijksmonumentnummer ?nr ; ceo:heeftGeometrie/ceo:asWKT-RD ?w }} GROUP BY ?nr"""),
    "rce_functions.csv": (RCE, PFX + f"""SELECT DISTINCT ?nr ?function WHERE {{ ?m ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <http://standaarden.overheid.nl/owms/terms/{NAME}_(gemeente)> ;
  ceo:rijksmonumentnummer ?nr ; ceo:heeftOorspronkelijkeFunctie/ceo:heeftFunctieNaam/skos:prefLabel ?function }}"""),
    "rce_styles.csv": (RCE, PFX + f"""SELECT DISTINCT ?nr ?style WHERE {{ ?m ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <http://standaarden.overheid.nl/owms/terms/{NAME}_(gemeente)> ;
  ceo:rijksmonumentnummer ?nr ; ceo:heeftStijlEnCultuur/ceo:heeftStijlEnCultuurNaam/skos:prefLabel ?style }}"""),
    "wd_monuments.csv": (WD, f"""SELECT ?i ?nr ?bag ?label ?inception ?image ?architectLabel WHERE {{
 ?i wdt:P359 ?nr ; wdt:P131* wd:{WIKIDATA} . OPTIONAL {{ ?i wdt:P5208 ?bag }} OPTIONAL {{ ?i wdt:P571 ?inception }}
 OPTIONAL {{ ?i wdt:P18 ?image }} OPTIONAL {{ ?i wdt:P84 ?architect }}
 OPTIONAL {{ ?i rdfs:label ?label FILTER(lang(?label)="nl") }}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "nl,en". }} }}"""),
    # Items in the municipality that are buildings, monuments or carry a BAG id; s06_wiki places them on a pand
    # by BAG id, else by monument number, else by their coordinates.
    "wd_buildings.csv": (WD, f"""SELECT ?i (SAMPLE(?bag0) AS ?bag) (SAMPLE(?nr0) AS ?nr) (SAMPLE(?c0) AS ?coord) ?labelEn ?labelNl
 (SAMPLE(?image0) AS ?image) ?en ?nl
 (GROUP_CONCAT(DISTINCT ?archLabel; separator="|") AS ?architects) (GROUP_CONCAT(DISTINCT ?styleLabel; separator="|") AS ?styles) WHERE {{
 ?i wdt:P131* wd:{WIKIDATA} .
 {{ ?i wdt:P5208 [] }} UNION {{ ?i wdt:P359 [] }} UNION {{ ?i wdt:P31/wdt:P279* wd:Q41176 }}
 OPTIONAL {{ ?i wdt:P5208 ?bag0 }} OPTIONAL {{ ?i wdt:P359 ?nr0 }} OPTIONAL {{ ?i wdt:P625 ?c0 }}
 OPTIONAL {{ ?i rdfs:label ?labelEn FILTER(lang(?labelEn)="en") }}
 OPTIONAL {{ ?i rdfs:label ?labelNl FILTER(lang(?labelNl)="nl") }}
 OPTIONAL {{ ?i wdt:P18 ?image0 }}
 OPTIONAL {{ ?en schema:about ?i ; schema:isPartOf <https://en.wikipedia.org/> }}
 OPTIONAL {{ ?nl schema:about ?i ; schema:isPartOf <https://nl.wikipedia.org/> }}
 OPTIONAL {{ ?i wdt:P84 ?a . ?a rdfs:label ?archLabel FILTER(lang(?archLabel)="en") }}
 OPTIONAL {{ ?i wdt:P149 ?s . ?s rdfs:label ?styleLabel FILTER(lang(?styleLabel)="en") }}
}} GROUP BY ?i ?labelEn ?labelNl ?en ?nl"""),
    "wd_relations.csv": (WD, f"""SELECT ?i ?bag ?label ?p ?vLabel ?article WHERE {{
 ?i wdt:P5208 ?bag . FILTER(STRSTARTS(?bag, "{GEMEENTE_CODE}"))
 VALUES ?p {{ wdt:P140 wdt:P127 wdt:P137 wdt:P466 wdt:P138 wdt:P31 wdt:P1435 wdt:P88 wdt:P495 wdt:P17 wdt:P2596 }}
 ?i ?p ?v .
 ?i rdfs:label ?label FILTER(lang(?label)="en" || lang(?label)="nl")
 OPTIONAL {{ ?article schema:about ?i ; schema:isPartOf <https://en.wikipedia.org/> }}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,nl". }} }}"""),
}


def main():
    for name, (endpoint, q) in QUERIES.items():
        if endpoint == RCE:
            r = requests.post(endpoint, data={"query": q}, headers={"Accept": "text/csv", **UA}, timeout=300)
        else:
            r = requests.get(endpoint, params={"query": q}, headers={"Accept": "text/csv", **UA}, timeout=300)
        r.raise_for_status()
        (RAW / name).write_text(r.text)
        print(name, len(list(csv.reader(io.StringIO(r.text)))) - 1)


if __name__ == "__main__":
    main()
