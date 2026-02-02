import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from polyjitter import jitter_points_within_polygons
from polyjitter._exceptions import CRSAlignmentError


def _simple_polygons() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        geometry=[
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
            Polygon([(3, 0), (5, 0), (5, 2), (3, 2)]),
        ],
        crs="EPSG:3857",
    )


def test_output_shape_matches_input() -> None:
    points = pd.Series(
        [Point(0.5, 0.5), Point(3.5, 0.5)],
        index=["a", "b"],
    )
    polygons = _simple_polygons()

    result = jitter_points_within_polygons(points, polygons, seed=1)

    assert isinstance(result, pd.Series)
    assert result.index.equals(points.index)
    assert len(result) == len(points)


def test_jittered_points_within_correct_polygons() -> None:
    points = pd.Series(
        [Point(1.0, 1.0), Point(4.0, 1.0)],
    )
    polygons = _simple_polygons()

    result = jitter_points_within_polygons(points, polygons, seed=42)

    for point, polygon in zip(result, polygons.geometry):
        assert point is not None
        assert polygon.contains(point)


def test_deterministic_with_fixed_seed() -> None:
    points = pd.Series([Point(1.0, 1.0)])
    polygons = _simple_polygons()

    r1 = jitter_points_within_polygons(points, polygons, seed=123)
    r2 = jitter_points_within_polygons(points, polygons, seed=123)

    assert r1.iloc[0].equals(r2.iloc[0])


def test_point_outside_all_polygons_returns_none() -> None:
    points = pd.Series([Point(10.0, 10.0)])
    polygons = _simple_polygons()

    result = jitter_points_within_polygons(points, polygons, seed=0)

    assert result.iloc[0] is None


def test_crs_mismatch_raises() -> None:
    points = gpd.GeoSeries(
        [Point(1.0, 1.0)],
        crs="EPSG:4326",
    )
    polygons = _simple_polygons()

    with pytest.raises(CRSAlignmentError):
        jitter_points_within_polygons(points, polygons)
