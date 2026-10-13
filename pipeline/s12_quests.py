"""Resolve every quest step to the buildings that answer it (web/data/quests.json) and check it can be solved.

A story answer takes the buildings of that story in data/curated.json; a group answer stays a rule the viewer
checks against the clicked building's layers; a year answer a rule on its year. A step fails when its story is
not found, its photo clue has no photo, or its group or year matches no building.
"""
import json
from pathlib import Path

import pandas as pd

from .quests import QUESTS


def main():
    curated = {L["id"]: L for L in json.load(open("data/curated.json"))}
    layers = {L["id"]: L for L in json.load(open("web/data/layers.json"))}
    wiki = json.load(open("web/data/wiki.json"))
    wk = pd.read_parquet("data/wiki_index.parquet").set_index("bag").wk
    years = pd.read_parquet("data/buildings.parquet", columns=["year"]).year
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
                step["answer"] = dict(bags=sorted({e["bag"] for e in es}))
                note = layers[layer]["notes"].get(es[0]["bag"], {})
                step["found"] = dict(name=es[0]["name"], story=es[0]["story"], source=es[0]["source"],
                                     story_nl=note.get("story_nl"), name_nl=note.get("name_nl"))
                if s.get("photo"):
                    photo = next((wiki[wk[b]]["image"] for b in step["answer"]["bags"]
                                  if b in wk.index and wiki[wk[b]].get("image")), None)
                    if not photo:
                        problems.append(f"{where}: no photo for {address}")
                        continue
                    step["photo"] = photo
            elif kind == "group":
                layer, group = arg
                g = next((g for g in layers.get(layer, {}).get("groups", []) if g["key"] == group), None)
                if not g or not g["count"]:
                    problems.append(f"{where}: group {layer}/{group} is empty")
                    continue
                step["answer"] = dict(layer=layer, bit=g["bit"])
            elif kind == "before":
                n = int((years < arg[0]).sum())
                if not n:
                    problems.append(f"{where}: no building before {arg[0]}")
                    continue
                step["answer"] = dict(before=arg[0])
            if s.get("layer") and s["layer"] not in layers:
                problems.append(f"{where}: hint layer {s['layer']} missing")
            steps.append(step)
        if len(steps) == len(q["steps"]):
            out.append(dict({k: v for k, v in q.items() if k != "steps"}, steps=steps))
        print(f'{q["id"]:10s} {len(steps)}/{len(q["steps"])}')
    for p in problems:
        print("problem:", p)
    Path("web/data/quests.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
