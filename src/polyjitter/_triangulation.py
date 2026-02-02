from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import triangulate
from polyjitter._exceptions import GeometryError


Triangles = Tuple[Tuple[Polygon, ...], np.ndarray]


def triangulate_polygon(polygon: Polygon) -> Triangles:
    """
    Triangulate a polygon and return triangles with area-based probabilities.
    """
    if not isinstance(polygon, Polygon):
        raise TypeError("geometry must be a shapely Polygon")

    triangles = tuple(triangulate(polygon))

    if not triangles:
        raise GeometryError("polygon triangulation produced no triangles")

    areas = np.array([t.area for t in triangles], dtype=float)

    if np.any(areas <= 0):
        raise ValueError("polygon contains degenerate triangles")

    probs = areas / areas.sum()

    return triangles, probs


def precompute_triangulations(
    polygons: Sequence[Polygon],
) -> Tuple[Triangles, ...]:
    """
    Precompute triangulations for a sequence of polygons.
    """
    return tuple(triangulate_polygon(polygon) for polygon in polygons)


def sample_point_from_triangle(
    triangle: Polygon,
    rng: np.random.Generator,
) -> Point:
    r1, r2 = rng.random(2)
    sqrt_r1 = np.sqrt(r1)

    (ax, ay), (bx, by), (cx, cy) = triangle.exterior.coords[:3]

    x = (1.0 - sqrt_r1) * ax + sqrt_r1 * (1.0 - r2) * bx + sqrt_r1 * r2 * cx
    y = (1.0 - sqrt_r1) * ay + sqrt_r1 * (1.0 - r2) * by + sqrt_r1 * r2 * cy

    return Point(x, y)


def random_point_in_polygon(
    triangles: Sequence[Polygon],
    probs: np.ndarray,
    rng: np.random.Generator,
) -> Point:
    """
    Sample a random point uniformly from within a polygon.
    """
    if len(triangles) == 0:
        raise ValueError("no triangles provided")

    triangle = triangles[int(rng.choice(len(triangles), p=probs))]
    return sample_point_from_triangle(triangle, rng)
