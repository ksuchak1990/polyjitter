import numpy as np
import pytest
from shapely.geometry import Point, Polygon

from polyjitter._triangulation import (
    precompute_triangulations,
    random_point_in_polygon,
    triangulate_polygon,
)


def test_triangulate_polygon_returns_valid_probabilities() -> None:
    polygon = Polygon(
        [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ]
    )

    triangles, probs = triangulate_polygon(polygon)

    assert len(triangles) > 0
    assert np.isclose(probs.sum(), 1.0)
    assert all(p > 0 for p in probs)


def test_random_point_is_within_polygon() -> None:
    polygon = Polygon(
        [
            (0.0, 0.0),
            (2.0, 0.0),
            (1.0, 1.5),
            (0.0, 1.0),
        ]
    )

    triangles, probs = triangulate_polygon(polygon)
    rng = np.random.default_rng(42)

    for _ in range(100):
        point = random_point_in_polygon(triangles, probs, rng)
        assert polygon.contains(point)


def test_precompute_triangulations_multiple_polygons() -> None:
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
    ]

    triangulations = precompute_triangulations(polygons)

    assert len(triangulations) == 2
    for triangles, probs in triangulations:
        assert len(triangles) > 0
        assert np.isclose(probs.sum(), 1.0)


def test_invalid_geometry_raises() -> None:
    with pytest.raises(TypeError):
        triangulate_polygon(Point(0, 0))  # type: ignore[arg-type]
