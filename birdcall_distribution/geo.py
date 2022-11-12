import numpy as np
import pandas as pd
from cartopy.io import shapereader
from shapely.geometry import Point, Polygon

CA_EXTENT = (-125, -114, 32, 43)


def get_shape_us_state(state_name):
    reader = shapereader.Reader(
        shapereader.natural_earth(
            resolution="50m", category="cultural", name="admin_1_states_provinces"
        )
    )
    shape = [
        s
        for s in reader.records()
        if s.attributes["admin"] == "United States of America"
        and s.attributes["name"] == state_name
    ][0]
    return shape


def generate_grid(shape, map_dims, grid_dims):
    """Generate a regular lattice of squares that cover a shape."""
    xmin, xmax, ymin, ymax = map_dims
    length, width = grid_dims

    # generate a grid of polygons that intersect with the provided shape
    polygons = {}
    cols = list(np.arange(xmin, xmax + width, width))
    rows = list(np.arange(ymin, ymax + length, length))
    for x in cols[:-1]:
        for y in rows[:-1]:
            polygon = Polygon(
                [(x, y), (x + width, y), (x + width, y + length), (x, y + length)]
            )
            if shape.geometry.intersects(polygon):
                polygons[f"{x}_{y}"] = polygon
    return polygons


def _maybe_get_polygon_pair(polygons, point):
    """Return the first polygon that contains a point."""
    for key, polygon in polygons.items():
        if polygon.contains(point):
            return key, polygon
    return None, None


def add_lonlat_columns(df, grid):
    """Add a grid columns to a dataframe."""
    pair = df.apply(
        lambda row: _maybe_get_polygon_pair(grid, Point(row.longitude, row.latitude)),
        axis="columns",
        result_type="expand",
    )
    pair.columns = ["grid_id", "grid"]
    df = pd.concat([df, pair], axis="columns")
    return df


def generate_grid_adjaceny_list(polygons):
    """We generate an adjacency list for the same grid of polygons we create.
    Find any intersecting polygons and add them to the adjacency list.
    """
    adj = {}
    for key, polygon in polygons.items():
        adj[key] = []
        for other_key, other_polygon in polygons.items():
            if key != other_key and polygon.intersects(other_polygon):
                adj[key].append(other_key)
    return adj


def get_adjacency_mapping(adjacency_list):
    """Get a mapping from grid keys to indices in the adjacency matrix."""
    keys = sorted(adjacency_list.keys())
    mapping = {key: i for i, key in enumerate(keys)}
    return mapping


def convert_to_adjacency_matrix(adjacency_list):
    """Convert the adjacency list to an adjacency matrix."""
    mapping = get_adjacency_mapping(adjacency_list)
    keys = sorted(adjacency_list.keys())

    n = len(mapping)
    W = np.zeros((n, n))
    for key in keys:
        i = mapping[key]
        for neighbor in adjacency_list[key]:
            j = mapping[neighbor]
            W[i, j] = 1
    return W.astype(int)
