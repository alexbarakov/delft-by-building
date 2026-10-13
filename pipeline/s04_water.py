"""Water (BGT waterdeel) and the city outline, in the viewer's local frame.

water.bin / land.bin layout (little-endian):
  u32 nPoly, nRing, nVert; u32 ringStart[nPoly+1]; u32 vertStart[nRing+1]; f32 xz[2*nVert]
First ring of each polygon is its exterior, the rest are holes.
"""
import struct
from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely

from .s03_tiles import DAM, to_local

OUT = Path("web/data")


def polygons(geom):
    return [g for g in getattr(geom, "geoms", [geom]) if g.geom_type == "Polygon" and not g.is_empty]


def pack(geoms) -> bytes:
    ring_start, vert_start, verts = [0], [0], []
    for poly in geoms:
        for ring in [poly.exterior, *poly.interiors]:
            c = shapely.get_coordinates(ring)[:-1]
            if len(c) < 3:
                continue
            verts.append(to_local(c).astype("<f4"))
            vert_start.append(vert_start[-1] + len(c))
        ring_start.append(len(vert_start) - 1)
    V = np.concatenate(verts)
    return (struct.pack("<3I", len(ring_start) - 1, len(vert_start) - 1, len(V))
            + np.array(ring_start, "<u4").tobytes() + np.array(vert_start, "<u4").tobytes() + V.tobytes())


def main():
    city = gpd.read_file("data/raw/boundary.json").set_crs(28992, allow_override=True).union_all()
    w = gpd.read_file("data/raw/bgt_waterdeel.geojson").set_crs(28992, allow_override=True)
    w = w[w.relatieve_hoogteligging == 0]
    water = shapely.make_valid(w.union_all()).intersection(city)
    water = water.buffer(0.5).buffer(-0.5).simplify(1.0)
    water = [p for p in polygons(water) if p.area > 30]
    land = city.difference(shapely.MultiPolygon(water)).simplify(1.0)
    land = [p for p in polygons(land) if p.area > 30]
    (OUT / "water.bin").write_bytes(pack(water))
    (OUT / "land.bin").write_bytes(pack(land))
    print(f"water {len(water)} polys {sum(p.area for p in water)/1e6:.1f} km², {(OUT/'water.bin').stat().st_size/1e6:.2f} MB;"
          f" land {len(land)} polys, {(OUT/'land.bin').stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
