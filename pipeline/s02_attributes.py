"""Dates, floors, heights per pand.

Date sources, in order of trust:
  exact      BAG oorspronkelijkbouwjaar as recorded
  faint      a pre-1800 round year in excess of what neighbouring years predict;
             spread across its rounding step
  estimated  BAG placeholder 1005, or an excess 1905 (a second, unofficial placeholder: the old centre
             holds ~10x more 1905 buildings than 1904 or 1906); median year of the nearest dated neighbours
  monument   a rijksmonument whose RCE date is earlier than BAG's (BAG often holds a rebuilding year);
             when BAG is earlier, BAG stays: the RCE date often describes a later facade;
             RCE year when it gives one, otherwise spread across its century or part of one
"""
import csv
import hashlib
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy.spatial import cKDTree

from .monuments import load as load_monuments
from .periods import period_index

PLACEHOLDER = 1005
FLAG_EXACT, FLAG_FAINT, FLAG_ESTIMATED, FLAG_MONUMENT, FLAG_MONUMENT_APPROX, FLAG_WIKIDATA, FLAG_1832 = 0, 1, 2, 3, 4, 5, 6
COVER_1832 = 0.6  # share of today's footprint that a building of the 1832 cadastre must cover
LATER_MARGIN = 10
SUSPECT_YEARS = ()
from .city import ORIGIN as DAM, ROUND_UNTIL
FLOORS_BAG3D, FLOORS_HEIGHT = 0, 1
STOREY_M = 3.2


def unit_hash(ids: pd.Series, salt: str) -> np.ndarray:
    """Deterministic uniform [0,1) per id, so reruns give the same picture."""
    return np.array([int(hashlib.md5((salt + i).encode()).hexdigest()[:8], 16) / 2**32 for i in ids])


def rounding_step(y: int) -> int:
    for step in (100, 50, 25, 10):
        if y % step == 0:
            return step
    return 1


def apply_monuments(p: pd.DataFrame) -> pd.DataFrame:
    """RCE wins where it contradicts BAG; where they agree, BAG's exact year stays."""
    links = load_monuments()
    bag = p.identificatie.str.slice(-16)
    u = unit_hash(p.identificatie, "monument")
    p["monument"] = bag.map(lambda b: links[b][2] if b in links else "")
    agree = disagree = 0
    for i in np.where(bag.isin(links))[0]:
        lo, hi, _ = links[bag.iat[i]]
        y = p.year.iat[i]
        if p.date_flag.iat[i] == FLAG_EXACT and y <= hi + LATER_MARGIN:
            agree += 1
            continue
        disagree += 1
        p.iat[i, p.columns.get_loc("year")] = lo if lo == hi else int(round(lo + u[i] * (hi - lo)))
        p.iat[i, p.columns.get_loc("date_flag")] = FLAG_MONUMENT if lo == hi else FLAG_MONUMENT_APPROX
    print(f"monuments: {agree} kept BAG, {disagree} redated")
    # Where RCE gives no date, a Wikidata inception more than ten years before BAG's year wins
    # (Hollandsche Schouwburg: BAG 1988, the rebuilding; built 1892). The earliest inception counts.
    inception = {}
    for r in csv.DictReader(open("data/raw/wd_monuments.csv")):
        if r["bag"] and r["inception"][:4].isdigit():
            k = r["bag"].zfill(16)
            inception[k] = min(inception.get(k, 9999), int(r["inception"][:4]))
    n = 0
    for i in np.where(~bag.isin(links) & bag.isin(inception))[0]:
        inc = inception[bag.iat[i]]
        if inc < p.year.iat[i] - LATER_MARGIN:
            p.iat[i, p.columns.get_loc("year")] = inc
            p.iat[i, p.columns.get_loc("date_flag")] = FLAG_WIKIDATA
            n += 1
    print(f"wikidata inception: {n} redated")
    return p


def smooth_round_years(p: pd.DataFrame) -> pd.DataFrame:
    """Before ROUND_UNTIL the register favours round years. Keep the expected count exact, fade the rest."""
    y = p.year.astype(int)
    counts = y.value_counts()
    u = unit_hash(p.identificatie, "round")
    u2 = unit_hash(p.identificatie, "spread")
    for year, n in counts.items():
        step = rounding_step(year)
        if year >= ROUND_UNTIL or step == 1:
            continue
        near = [counts.get(year + d, 0) for d in range(-4, 5) if d and rounding_step(year + d) == 1]
        expected = max(1.0, float(np.mean(near))) if near else 1.0
        if n <= expected:
            continue
        idx = np.where((y.values == year) & (p.date_flag.values == FLAG_EXACT))[0]
        order = idx[np.argsort(u[idx])]
        faint = order[int(round(expected)):]
        half = step / 2
        p.iloc[faint, p.columns.get_loc("year")] = np.round(year - half + u2[faint] * step).astype(int)
        p.iloc[faint, p.columns.get_loc("date_flag")] = FLAG_FAINT
    return p


def flag_suspect_years(p: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Keep as many buildings on a suspect year as the neighbouring years predict; the excess,
    taken nearest the Dam first (where the placeholder concentrates), becomes estimated."""
    y = p.year.values
    exact = p.date_flag.values == FLAG_EXACT
    dist = np.hypot(p.geometry.centroid.x - DAM[0], p.geometry.centroid.y - DAM[1]).values
    for year in SUSPECT_YEARS:
        expected = np.mean([((y == year + d) & exact).sum() for d in (-3, -2, -1, 1, 2, 3)])
        idx = np.where((y == year) & exact)[0]
        excess = idx[np.argsort(dist[idx])][: max(0, len(idx) - int(round(expected)))]
        p.iloc[excess, p.columns.get_loc("date_flag")] = FLAG_ESTIMATED
        print(f"{year}: {len(idx)} on record, {expected:.0f} expected, {len(excess)} estimated")
    return p


def estimate_placeholders(p: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    pts = np.c_[p.geometry.centroid.x, p.geometry.centroid.y]
    known = p.date_flag.values != FLAG_ESTIMATED
    tree = cKDTree(pts[known])
    years = p.year.values[known]
    todo = np.where(~known)[0]
    dist, nn = tree.query(pts[todo], k=12, distance_upper_bound=1000)
    for row, d, n in zip(todo, dist, nn):
        ok = np.isfinite(d)
        p.iat[row, p.columns.get_loc("year")] = int(np.median(years[n[ok]])) if ok.any() else 1900
    return p


def flag_1832(p: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """A building BAG dates after 1832 that stands on the footprint of a building in the 1832 cadastre may be older
    than BAG says (BAG often records a rebuilding), or may have replaced it on the same plot. The year stays;
    the building is drawn paler and its card says so. Only exact BAG years are flagged."""
    old = gpd.read_file("data/raw/layers/gebouwen_1832.geojson").set_crs(28992, allow_override=True)
    old["geometry"] = old.geometry.make_valid()
    geom = p.geometry.make_valid()
    cand = np.where((p.year.values > 1832) & (p.date_flag.values == FLAG_EXACT))[0]
    j = gpd.sjoin(gpd.GeoDataFrame(geometry=geom.iloc[cand].values, index=cand, crs=28992), old[["geometry"]],
                  predicate="intersects")
    hit = []
    for i, grp in j.groupby(level=0):
        g = geom.iat[i]
        covered = shapely.union_all(old.geometry.iloc[grp.index_right].values).intersection(g).area
        if covered >= COVER_1832 * g.area:
            hit.append(i)
    p.iloc[hit, p.columns.get_loc("date_flag")] = FLAG_1832
    yrs = p.year.iloc[hit]
    print(f"1832 footprints: {len(hit)} buildings dated after 1832 stand on one ({(yrs <= 1900).sum()} up to 1900)")
    return p


def main():
    p = gpd.read_parquet("data/panden.parquet")
    q = gpd.read_parquet("data/parts.parquet")

    p["year"] = p.oorspronkelijkbouwjaar.astype(int)
    p["date_flag"] = np.where(p.year == PLACEHOLDER, FLAG_ESTIMATED, FLAG_EXACT).astype(np.uint8)
    p = apply_monuments(p)
    p = flag_1832(p)
    p = flag_suspect_years(p)
    p = smooth_round_years(p)
    p = estimate_placeholders(p)
    p["period"] = p.year.map(period_index).astype(np.uint8)

    # Height: tallest LoD1.3 part's 70th-percentile roof above ground.
    top = q.groupby("identificatie").b3_h_70p.max()
    p["h_roof"] = p.identificatie.map(top)
    p["height"] = (p.h_roof - p.b3_h_maaiveld).clip(lower=2.5)

    by_height = np.clip(np.round(p.height / STOREY_M), 1, 99)
    bag3d = p.b3_bouwlagen
    # b3_bouwlagen is capped at 5 and only modelled for simple roofs; trust it below the cap only.
    use_bag3d = bag3d.notna() & (bag3d < 5)
    p["floors"] = np.where(use_bag3d, bag3d, by_height).astype(np.uint8)
    p["floors_src"] = np.where(use_bag3d, FLOORS_BAG3D, FLOORS_HEIGHT).astype(np.uint8)

    p = p.sort_values("identificatie").reset_index(drop=True)
    p.to_parquet("data/buildings.parquet")

    stats = {
        "buildings": len(p),
        "exact": int((p.date_flag == FLAG_EXACT).sum()),
        "faint_round": int((p.date_flag == FLAG_FAINT).sum()),
        "estimated": int((p.date_flag == FLAG_ESTIMATED).sum()),
        "monument": int((p.date_flag == FLAG_MONUMENT).sum()),
        "monument_approx": int((p.date_flag == FLAG_MONUMENT_APPROX).sum()),
        "floors_bag3d": int((p.floors_src == FLOORS_BAG3D).sum()),
        "floors_height": int((p.floors_src == FLOORS_HEIGHT).sum()),
    }
    print(stats)
    print(p.groupby("period").size().to_dict())


if __name__ == "__main__":
    main()
