"""Well-known residents: people whose Dutch Wikipedia article names the Delft address they lived or worked at.

1. Wikidata: people tied to the city (born, died, lived or worked there) with a Dutch Wikipedia article.
2. Their article's wikitext is searched for a street name of the city followed by a house number, in a
   sentence about living, moving, dying or working there.
3. The address is geocoded to a BAG building (local BAG addresses, exact house number).
The sentence is kept as the source quote; house numbers can have changed since the person lived there.
"""
import json
from concurrent.futures import ThreadPoolExecutor
import re
import time
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import Point

from .city import NAME, UA, WIKIDATA
from .geo import lookup, streets as all_streets
VERBS = re.compile(r"\b(woonde|woonden|woont|bewoonde|verhuisde|betrok|vestigde|kocht|overleed|stierf|geboren|"
                   r"atelier|werkte|huis aan|woning aan|woonhuis|pand aan|leefde|groeide op|woonachtig|"
                   r"in het pand|in het huis|geboortehuis|sterfhuis|op nummer)\b", re.I)
SELF = re.compile(r"\b(hij|zij|ze|het gezin|het echtpaar|de familie|het paar)\b", re.I)


def people():
    q = """SELECT ?p ?pLabel ?article ?desc ?born ?died ?img (MAX(?sl) AS ?links) WHERE {
      VALUES ?prop { wdt:P19 wdt:P20 wdt:P551 wdt:P937 }
      ?p ?prop wd:%s ; wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
      FILTER(?sl >= 3)
      ?article schema:about ?p ; schema:isPartOf <https://nl.wikipedia.org/> .
      OPTIONAL { ?p schema:description ?desc FILTER(lang(?desc)="en") }
      OPTIONAL { ?p wdt:P569 ?born } OPTIONAL { ?p wdt:P570 ?died } OPTIONAL { ?p wdt:P18 ?img }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,nl". }
    } GROUP BY ?p ?pLabel ?article ?desc ?born ?died ?img"""
    r = requests.get("https://query.wikidata.org/sparql", params={"query": q % WIKIDATA, "format": "json"}, headers=UA, timeout=300)
    out = {}
    for b in r.json()["results"]["bindings"]:
        v = {k: x["value"] for k, x in b.items()}
        out.setdefault(v["p"], v)
    return list(out.values())


def street_hits(streets):
    """Dutch Wikipedia articles whose source has '<street> <number>', found with a regex search per street."""
    cache = Path("data/raw/nlwiki_street_hits.json")
    hits = json.loads(cache.read_text()) if cache.exists() else {}
    def one(st):
        titles, offset = [], 0
        while offset is not None:
            for attempt in range(5):
                r = requests.get("https://nl.wikipedia.org/w/api.php", headers=UA, timeout=120, params={
                    "action": "query", "list": "search", "format": "json", "srlimit": 500, "srprop": "",
                    "sroffset": offset, "srnamespace": 0, "srsearch": f'insource:/{st} [0-9]/'})
                if r.ok and "query" in r.json():
                    break
                time.sleep(3 * 2 ** attempt)
            d = r.json()
            titles += [x["title"] for x in d.get("query", {}).get("search", [])]
            offset = d.get("continue", {}).get("sroffset")
            time.sleep(0.5)
        return st, titles

    todo = [st for st in streets if st not in hits]
    with ThreadPoolExecutor(3) as ex:
        for i, (st, titles) in enumerate(ex.map(one, todo)):
            hits[st] = titles
            if i % 20 == 0:
                cache.write_text(json.dumps(hits, ensure_ascii=False))
    cache.write_text(json.dumps(hits, ensure_ascii=False))
    return hits


def humans(titles):
    """Keep the titles whose Wikidata item is a person, with the same fields people() returns."""
    out = []
    for i in range(0, len(titles), 200):
        vals = " ".join(f'<https://nl.wikipedia.org/wiki/{requests.utils.quote(t.replace(" ", "_"), safe="")}>' for t in titles[i:i + 200])
        q = f"""SELECT ?p ?pLabel ?article ?desc ?born ?died ?img (MAX(?sl) AS ?links) WHERE {{
          VALUES ?article {{ {vals} }} ?article schema:about ?p . ?p wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
          OPTIONAL {{ ?p schema:description ?desc FILTER(lang(?desc)="en") }}
          OPTIONAL {{ ?p wdt:P569 ?born }} OPTIONAL {{ ?p wdt:P570 ?died }} OPTIONAL {{ ?p wdt:P18 ?img }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,nl". }}
        }} GROUP BY ?p ?pLabel ?article ?desc ?born ?died ?img"""
        r = requests.post("https://query.wikidata.org/sparql", data={"query": q, "format": "json"}, headers=UA, timeout=300)
        seen = set()
        for b in r.json()["results"]["bindings"]:
            v = {k: x["value"] for k, x in b.items()}
            if v["p"] not in seen:
                seen.add(v["p"]); out.append(v)
        time.sleep(1)
    return out


def wikitexts(titles):
    texts = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        for attempt in range(5):
            r = requests.get("https://nl.wikipedia.org/w/api.php", headers=UA, timeout=120, params={
                "action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "format": "json",
                "formatversion": 2, "redirects": 1, "titles": "|".join(chunk)})
            if r.ok and r.headers.get("content-type", "").startswith("application/json"):
                break
            time.sleep(2 ** attempt)
        d = r.json()["query"]
        back = {n["to"]: n["from"] for n in d.get("normalized", []) + d.get("redirects", [])}
        for p in d["pages"]:
            t = p["title"]
            while t in back:
                t = back[t]
            if p.get("revisions"):
                texts[t] = p["revisions"][0]["slots"]["main"]["content"]
        time.sleep(0.3)
    return texts


# Institutions whose Wikidata item sits on a newer building than the one a biography means (the Oude Gasthuis on the Koornmarkt).
REJECTED = []
MOVED = {"Reinier de Graaf Gasthuis"}
BUILDING_ARTICLES = {}  # nl Wikipedia title → BAG ids of the building the article is about (Wikidata P5208)


def building_articles():
    for it in json.load(open("data/wd_places.json")).values():
        if it["nl"]:
            t = requests.utils.unquote(it["nl"].rsplit("/wiki/", 1)[1]).replace("_", " ")
            BUILDING_ARTICLES.setdefault(t, set()).update(it["bags"])


def mark_buildings(wt):
    """Links to building articles become ⟦title⟧ markers, so a sentence can point at a building by name
    (the Rembrandthuis) as well as by address."""
    def repl(m):
        title = m.group(1).strip()
        title = title[:1].upper() + title[1:]
        text = m.group(2) or m.group(1)
        return f"⟦{title}⟧{text}" if title in BUILDING_ARTICLES else m.group(0)
    return re.sub(r"\[\[([^|\]#]+)(?:\|([^\]]*))?\]\]", repl, wt)


def clean(wt):
    """Wikitext to plain sentences; headings become sentence breaks so a quote never spans sections."""
    wt = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", wt, flags=re.S)
    for _ in range(3):
        wt = re.sub(r"\{\{[^{}]*\}\}", "", wt)
    wt = re.sub(r"\[\[(?:Bestand|File|Afbeelding|Categorie|Image):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", wt, flags=re.I)
    wt = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", wt)
    wt = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", wt)
    wt = re.sub(r"^=+[^=\n]*=+\s*$", ". ", wt, flags=re.M)
    wt = re.sub(r"^[*#:;|!{].*$", ". ", wt, flags=re.M)
    wt = re.sub(r"<[^>]+>|'{2,}|thumb\|", "", wt)
    return re.sub(r"\s+", " ", wt)


GEO = {}


def geocode(address, buildings=None):
    hit = lookup(address)
    return hit[0] if hit else None


def residents_by_wikidata():
    """People whose Wikidata residence, workplace, birth or death place is one of the placed buildings."""
    places = json.load(open("data/wd_places.json"))
    vals = " ".join(f"<{i}>" for i in places)
    q = f"""SELECT ?person ?personLabel ?prop ?b ?desc ?born ?died ?img WHERE {{
      VALUES ?b {{ {vals} }} VALUES ?prop {{ wdt:P551 wdt:P937 wdt:P19 wdt:P20 }}
      ?person ?prop ?b ; wdt:P31 wd:Q5 .
      OPTIONAL {{ ?person schema:description ?desc FILTER(lang(?desc)="en") }}
      OPTIONAL {{ ?person wdt:P569 ?born }} OPTIONAL {{ ?person wdt:P570 ?died }} OPTIONAL {{ ?person wdt:P18 ?img }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,nl". }} }}"""
    r = requests.post("https://query.wikidata.org/sparql", data={"query": q, "format": "json"}, headers=UA, timeout=300)
    out = []
    for x in r.json()["results"]["bindings"]:
        v = {k: y["value"] for k, y in x.items()}
        if re.fullmatch(r"Q\d+", v["personLabel"]):  # no name in English or Dutch
            continue
        for bag in places[v["b"]]["bags"]:
            out.append(dict(v, bag=bag, desc=v.get("desc", ""), born=v.get("born", ""), died=v.get("died", ""), img=v.get("img", "")))
    return out


def main():
    building_articles()
    ppl = people()
    tied = {p["p"] for p in ppl}
    labels = json.load(open("web/data/labels.json"))
    # Streets worth a search: the named canals and main streets, and every street within 2.5 km of the Dam.
    near = sorted({l["name"] for l in labels if len(l["name"]) > 4 and
                   (l["tier"] == 1 or min(x * x + z * z for x, z, *_ in l["pts"]) < 2500 ** 2)})
    hits = street_hits(near)
    extra = sorted({t for ts in hits.values() for t in ts})
    known = {requests.utils.unquote(p["article"].rsplit("/wiki/", 1)[1]).replace("_", " ") for p in ppl}
    ppl += humans([t for t in extra if t not in known])
    print(len(ppl), "people,", len(near), "streets searched")
    titles = sorted({requests.utils.unquote(p["article"].rsplit("/wiki/", 1)[1]).replace("_", " ") for p in ppl})
    texts = wikitexts(titles)
    print(len(texts), "articles")
    streets = [s for s in all_streets() if len(s) > 4]
    addr_re = re.compile(r"\b(" + "|".join(map(re.escape, streets)) + r")\s+(\d{1,4}[a-z]?)\b")
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "geometry"])
    b["bag"] = b.identificatie.str.slice(-16)

    found = []
    for p in ppl:
        title = requests.utils.unquote(p["article"].rsplit("/wiki/", 1)[1]).replace("_", " ")
        text = clean(mark_buildings(texts.get(title, "")))
        seen = set()
        surname = p["pLabel"].split()[-1].lower()
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text):
            if not VERBS.search(sentence) or len(sentence) > 400:
                continue
            # The sentence must be about this person: their surname, or a pronoun opening it.
            if surname not in sentence.lower() and not SELF.match(sentence.strip()):
                continue
            quote = re.sub(r"⟦[^⟧]*⟧", "", sentence).strip()[:400]
            # a church named in a sentence about a burial is where they lie, not where they lived
            # ... and one named for a wedding, a baptism or as a landmark nearby is not a home either
            buried = re.search(r"\b(begraven|bijgezet|begraafplaats|graf|grafkelder|trouwde|huwelijk|gedoopt|"
                               r"nabij|naast|tegenover|bij de)\b", sentence, re.I)
            for t in ([] if buried else re.findall(r"⟦([^⟧]*)⟧", sentence)):
                if t in MOVED:
                    continue
                for bag in BUILDING_ARTICLES[t]:
                    if ("article", bag) not in seen:
                        seen.add(("article", bag))
                        found.append(dict(bag=bag, address=t, person=p["pLabel"], wikidata=p["p"], url=p["article"],
                                          desc=p.get("desc"), born=(p.get("born") or "")[:4], died=(p.get("died") or "")[:4],
                                          img=p.get("img"), links=int(p["links"]), quote=quote))
            # Street names repeat across the country: an address counts only in a sentence that names no other town,
            # and, unless it names the city itself, only for people Wikidata ties to the city or whose article keeps
            # coming back to it.
            plain = re.sub(r"⟦[^⟧]*⟧", "", sentence)
            towns = {t for t in re.findall(r"\b(?:in|te|naar|uit|bij)\s+((?:Den |'s-)?[A-Z][a-zë]+(?:[- ][A-Z][a-z]+)?)", plain)}
            if towns - {NAME} or (NAME not in plain and p["p"] not in tied and text.count(NAME) < 3):
                if re.search(addr_re, plain):
                    REJECTED.append((p["pLabel"], sorted(towns - {NAME}), p["p"] in tied, plain[:160]))
                continue
            for m in re.finditer(addr_re, plain):
                address = f"{m.group(1)} {m.group(2)}"
                if address in seen:
                    continue
                seen.add(address)
                bag = geocode(address, b)
                if bag:
                    found.append(dict(bag=bag, address=address, person=p["pLabel"], wikidata=p["p"],
                                      url=p["article"], desc=p.get("desc"), born=(p.get("born") or "")[:4],
                                      died=(p.get("died") or "")[:4], img=p.get("img"),
                                      links=int(p["links"]), quote=quote))
    import csv
    for r in residents_by_wikidata():
        why = {"P551": "Wikidata records this building as their residence.",
               "P937": "Wikidata records this building as their place of work.",
               "P19": "Wikidata records this building as their birthplace.",
               "P20": "Wikidata records this building as the place where they died."}[r["prop"].rsplit("/", 1)[1]]
        found.append(dict(bag=r["bag"], address="", person=r["personLabel"], wikidata=r["person"],
                          url=r["person"], desc=r["desc"], born=r["born"][:4], died=r["died"][:4], img=r["img"],
                          links=0, quote=why))
    uniq = {}
    for f in found:  # one entry per person and building; Wikipedia quotes come first, so they win
        uniq.setdefault((f["bag"], f["person"]), f)
    found = sorted(uniq.values(), key=lambda f: -f["links"])
    Path("data/residents_rejected.json").write_text(json.dumps(REJECTED, ensure_ascii=False, indent=1))
    Path("data/residents.json").write_text(json.dumps(found, ensure_ascii=False, indent=1))
    print(len(found), "addresses;", len({f["person"] for f in found}), "people;", len({f["bag"] for f in found}), "buildings")


if __name__ == "__main__":
    main()
