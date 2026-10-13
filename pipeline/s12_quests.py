"""Resolve every quest step to the buildings that answer it (web/data/quests.json) and check it can be solved.

A story answer takes the buildings of that story in data/curated.json and gets a second hint, its direction and
distance from the Markt, computed here so it is always right. A rule answer stays a rule the viewer checks against
the clicked building (layer groups by bit, years). A step fails when its story is not found, its photo clue has no
photo, or its rule matches no building; a quest with a failed step is left out.
"""
import json
import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from .city import ORIGIN
from .quests import QUESTS

DIRS = [("east", "oosten"), ("north-east", "noordoosten"), ("north", "noorden"), ("north-west", "noordwesten"),
        ("west", "westen"), ("south-west", "zuidwesten"), ("south", "zuiden"), ("south-east", "zuidoosten")]


def direction_hint(x, y):
    dx, dy = x - ORIGIN[0], y - ORIGIN[1]
    d = math.hypot(dx, dy)
    if d < 120:
        return dict(en="It is right by the Markt.", nl="Het staat vlak bij de Markt.")
    en, nl = DIRS[round(math.degrees(math.atan2(dy, dx)) / 45) % 8]
    if d < 1000:
        unit_en = unit_nl = f"{int(round(d / 50) * 50)} m"
    else:
        r = round(d / 100) / 10
        unit_en, unit_nl = f"{r} km", f"{str(r).replace('.', ',')} km"
    return dict(en=f"It is about {unit_en} {en} of the Markt.", nl=f"Het staat zo’n {unit_nl} ten {nl} van de Markt.")


def main():
    curated = {L["id"]: L for L in json.load(open("data/curated.json"))}
    layers = {L["id"]: L for L in json.load(open("web/data/layers.json"))}
    wiki = json.load(open("web/data/wiki.json"))
    wk = pd.read_parquet("data/wiki_index.parquet").set_index("bag").wk
    b = gpd.read_parquet("data/buildings.parquet", columns=["identificatie", "year", "geometry"])
    bag = b.identificatie.str.slice(-16).to_numpy()
    c = b.geometry.centroid
    xy = dict(zip(bag, zip(c.x, c.y)))
    lay = pd.read_parquet("data/layers.parquet")
    assert (lay.identificatie.to_numpy() == b.identificatie.to_numpy()).all()
    mask = (lay.lay1.to_numpy(np.uint64) << np.uint64(32)) | lay.lay0.to_numpy(np.uint64)
    out, problems = [], []
    for q in QUESTS:
        steps = []
        for i, s in enumerate(q["steps"]):
            kind, *arg = s["answer"]
            step = {k: v for k, v in s.items() if k != "answer"}
            where = f'{q["id"]} step {i + 1}'
            if kind == "story":
                layer, address = arg
                es = [e for e in curated.get(layer, {}).get("entries", []) if e["address"] == address]
                if not es:
                    problems.append(f"{where}: no story at {address} in {layer}")
                    continue
                bags = sorted({e["bag"] for e in es})
                step["answer"] = dict(bags=bags)
                note = layers[layer]["notes"].get(es[0]["bag"], {})
                step["found"] = dict(name=es[0]["name"], story=es[0]["story"], source=es[0]["source"],
                                     story_nl=note.get("story_nl"), name_nl=note.get("name_nl"))
                x, y = np.mean([xy[k] for k in bags if k in xy], axis=0)
                auto = direction_hint(x, y)
                said = " ".join([s["riddle"]["en"]] + [h["en"] for h in s["hints"]])
                if "right by the Markt" in auto["en"] and "Markt" in said:
                    step["hints"] = s["hints"]  # the riddle already places it on the Markt
                # Hard quests open with the vaguer hint, the others end with it.
                elif q["level"] == 3:
                    step["hints"] = [auto] + s["hints"]
                else:
                    step["hints"] = s["hints"] + [auto]
                if s.get("photo"):
                    photo = next((wiki[wk[k]]["image"] for k in bags if k in wk.index and wiki[wk[k]].get("image")), None)
                    if not photo:
                        problems.append(f"{where}: no photo for {address}")
                        continue
                    step["photo"] = photo
            elif kind == "rule":
                rule, ok, cond = arg[0], np.ones(len(b), bool), {}
                if "before" in rule:
                    ok &= b.year.to_numpy() < rule["before"]
                    cond["before"] = rule["before"]
                if "after" in rule:
                    ok &= b.year.to_numpy() > rule["after"]
                    cond["after"] = rule["after"]
                bits = []
                for layer, group in rule.get("groups", []):
                    g = next((g for g in layers.get(layer, {}).get("groups", []) if g["key"] == group), None)
                    if not g:
                        problems.append(f"{where}: no group {layer}/{group}")
                        ok[:] = False
                        break
                    ok &= ((mask >> np.uint64(g["bit"])) & np.uint64(1)).astype(bool)
                    bits.append(g["bit"])
                if bits:
                    cond["bits"] = bits
                if not ok.any():
                    problems.append(f"{where}: no building meets {rule}")
                    continue
                step["answer"] = cond
                step["count"] = int(ok.sum())
            if s.get("layer") and s["layer"] not in layers:
                problems.append(f"{where}: hint layer {s['layer']} missing")
            steps.append(step)
        if len(steps) == len(q["steps"]):
            out.append(dict({k: v for k, v in q.items() if k != "steps"}, steps=steps))
        print(f'{q["id"]:10s} level {q["level"]}  {len(steps)}/{len(q["steps"])}')
    for p in problems:
        print("problem:", p)
    Path("web/data/quests.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(len(out), "quests")


if __name__ == "__main__":
    main()
