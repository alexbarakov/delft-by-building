"""Check every 'Did you know' fact against its article and attach it to the building (web/data/facts.json)."""
import json
from pathlib import Path

from .facts import FACTS
from .s08_curated import article, geocode, wikidata_bags


def main():
    out, dropped = {}, []
    for ref, en, nl, checks, *where in FACTS:
        text, url = article(ref)
        missing = [c for c in checks if c.lower() not in text.lower()]
        # the building: the article's own Wikidata item, another article's, or an address
        place = where[0] if where else ref
        if place.startswith("addr:"):
            bag, _ = geocode(place[5:])
            bags = {bag} if bag else set()
        else:
            bags = wikidata_bags().get(article(place)[1], set())
        if missing or not bags:
            dropped.append((ref, missing, "no BAG id in Wikidata" if not bags else ""))
            continue
        for bag in bags:
            out[bag] = {"en": en, "nl": nl, "source": url}
    Path("web/data/facts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"{len(FACTS) - len(dropped)}/{len(FACTS)} facts on {len(out)} buildings")
    for d in dropped:
        print("dropped:", d)


if __name__ == "__main__":
    main()
