from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.geometry import Polygon
from typing import cast


from polyjitter._triangulation import (
    precompute_triangulations,
    random_point_in_polygon,
)
from polyjitter._exceptions import InvalidInputError, CRSAlignmentError


def _validate_inputs(
    points: pd.Series,
    polygons: gpd.GeoDataFrame,
) -> None:
    if not isinstance(points, pd.Series):
        raise InvalidInputError("points must be a pandas Series")

    if not isinstance(polygons, gpd.GeoDataFrame):
        raise TypeError("polygons must be a GeoDataFrame")

    if "geometry" not in polygons.columns:
        raise ValueError("polygons must have a geometry column")

    if polygons.crs is None:
        raise ValueError("polygons GeoDataFrame must have a CRS")

    if not all(isinstance(p, Point) or p is None for p in points):
        raise TypeError("points must contain shapely Point geometries or None")

    points_crs = getattr(points, "crs", None)
    if points_crs is not None and points_crs != polygons.crs:
        raise CRSAlignmentError("points CRS must match polygons CRS")


def _spatial_join(
    points: pd.Series,
    polygons: gpd.GeoDataFrame,
) -> pd.Series:
    points_gs = gpd.GeoSeries(
        points,
        index=points.index,
        crs=polygons.crs,
    )

    joined = gpd.sjoin(
        gpd.GeoDataFrame(geometry=points_gs),
        polygons[["geometry"]],
        how="left",
        predicate="within",
    )

    return joined["index_right"]


def jitter_points_within_polygons(
    points: pd.Series,
    polygons: gpd.GeoDataFrame,
    *,
    seed: int | None = None,
) -> pd.Series:
    _validate_inputs(points, polygons)

    polygons = polygons.reset_index(drop=True)

    rng = np.random.default_rng(seed)

    point_to_polygon = _spatial_join(points, polygons)

    geoms = cast(list[Polygon], polygons.geometry.to_list())
    triangulations = precompute_triangulations(geoms)

    jittered = pd.Series(index=points.index, dtype=object)

    poly_idxs = point_to_polygon.to_numpy()

    for i, poly_idx in enumerate(poly_idxs):
        if pd.isna(poly_idx):
            jittered.iloc[i] = None
            continue

        triangles, probs = triangulations[int(poly_idx)]
        jittered.iloc[i] = random_point_in_polygon(
            triangles=triangles,
            probs=probs,
            rng=rng,
        )

    return jittered
