# `polyjitter`

Uniformly jitter point geometries within polygon boundaries.

`polyjitter` provides a small, deterministic utility for resampling point
locations such that each point is moved to a new, random location **within the
polygon that originally contained it**.
The primary goal is to introduce spatial jitter **without ever crossing polygon
boundaries**.

The implementation is geometry-correct, efficient, and designed to scale to
large datasets.

## What it does

Given:

- a `pandas.Series` of Shapely `Point` geometries, and
- a `geopandas.GeoDataFrame` of **mutually exclusive** polygon geometries,

`polyjitter`:

1. Spatially joins each point to its containing polygon
2. Uniformly samples a new point from within that polygon
3. Returns a Series of jittered points aligned to the input index

## Goals

- **No boundary crossing:** Jittered points are guaranteed to lie within the
  original containing polygon.
- **Uniform sampling:** Points are sampled uniformly over polygon area (not
  bounding boxes).
- **Deterministic with seed:** Supplying a seed produces reproducible results.
- **One spatial join per call:** Designed to be efficient for large numbers of
  points.

## Non-goals

`polyjitter` does not attempt to provide:

- Distance-based jitter controls
- Privacy or anonymisation guarantees
- CRS transformation or reprojection
- Support for non-polygon geometries
- Heuristic or approximate sampling

The package focuses strictly on correct geometry and predictable behaviour.

## Installation

The package is not yet published to PyPI.

For local development:

```bash
git clone https://github.com/ksuchak1990/polyjitter.git
cd polyjitter
uv pip install -e .
```

## Usage

```{python}
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from polyjitter import jitter_points_within_polygons

points = pd.Series([
    Point(1.0, 1.0),
    Point(4.0, 1.0),
])

polygons = gpd.GeoDataFrame(
    geometry=[...],
    crs="EPSG:3857",
)

jittered = jitter_points_within_polygons(points, polygons, seed=42)
```

Points that do not fall within any polygon will return `None`.
