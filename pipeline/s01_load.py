"""Load 3D BAG tiles, clip to Amsterdam, keep one row per pand + LoD1.3 parts."""
import glob
import geopandas as gpd
import pandas as pd
import pyogrio

PAND_COLS = ["identificatie", "oorspronkelijkbouwjaar", "status", "b3_bouwlagen",
             "b3_h_maaiveld", "b3_h_dak_50p", "b3_h_dak_70p", "b3_h_dak_max",
             "b3_dak_type", "b3_opp_grond", "b3_kwaliteitsindicator", "b3_pw_datum"]

def main():
    boundary = gpd.read_file("data/raw/boundary.json").set_crs(28992, allow_override=True)
    city = boundary.union_all()
    panden, parts = [], []
    for f in sorted(glob.glob("data/raw/3dbag/*.gpkg")):
        p = pyogrio.read_dataframe(f, layer="pand", columns=PAND_COLS)
        q = pyogrio.read_dataframe(f, layer="lod13_2d")
        panden.append(p); parts.append(q)
    p = pd.concat(panden).drop_duplicates("identificatie")
    p = gpd.GeoDataFrame(p, geometry="geometry", crs=28992)
    p = p[p.representative_point().within(city)]
    q = gpd.GeoDataFrame(pd.concat(parts), geometry="geometry", crs=28992)
    q = q[q.identificatie.isin(p.identificatie)].drop_duplicates(["identificatie", "b3_pand_deel_id", "b3_dd_id"])
    p.to_parquet("data/panden.parquet"); q.to_parquet("data/parts.parquet")
    print(len(p), "panden;", len(q), "lod13 parts")

if __name__ == "__main__":
    main()
