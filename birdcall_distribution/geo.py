import numpy as np
from cartopy.io import shapereader
from shapely.geometry import Polygon


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
