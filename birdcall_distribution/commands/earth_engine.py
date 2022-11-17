from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool

import ee
import pandas as pd
from shapely.geometry import mapping
from tqdm.auto import tqdm

from birdcall_distribution.geo import (
    CA_EXTENT,
    WESTERN_US_EXTENT,
    generate_grid,
    get_california_geometry,
    get_western_us_geometry,
)


def t_modis_to_celsius(t_modis):
    """Converts MODIS LST units to degrees Celsius."""
    if t_modis is None:
        return None
    t_celsius = 0.02 * t_modis - 273.15
    return t_celsius


def get_stats(grid, key, start_ds="2019-01-01", end_ds="2022-01-01", scale=1000):
    """Get statistics for population, elevation, temperature, and land cover."""
    geojson = mapping(grid[key])
    poi = ee.Geometry.Polygon(geojson["coordinates"])

    # population
    population_density = (
        ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Density")
        .select("population_density")
        .limit(1, "system:time_start", False)
        .first()
        .reduceRegion(ee.Reducer.sum(), poi, scale)
        .getInfo()
    )

    # Import the USGS ground elevation image.
    elevation = (
        ee.Image("USGS/SRTMGL1_003")
        .select("elevation")
        .reduceRegion(
            ee.Reducer.percentile([5, 50, 95]),
            poi,
            scale=scale,
        )
        .getInfo()
    )

    # Import the MODIS land surface temperature collection.
    # temperature day and night, with quality control bands
    # we need to filter it first
    surface_temp = (
        ee.ImageCollection("MODIS/006/MOD11A1")
        .select("LST_Day_1km", "LST_Night_1km")
        .filterDate(start_ds, end_ds)
        .mean()
        .reduceRegion(
            ee.Reducer.percentile([5, 50, 95]),
            poi,
            scale=scale,
        )
        .getInfo()
    )

    # Import the MODIS land cover collection.
    # https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MCD12Q1#bands
    land_cover = (
        ee.ImageCollection("MODIS/006/MCD12Q1")
        .first()
        .sample(poi, scale)
        .aggregate_histogram("LC_Type1")
        .getInfo()
    )

    # count the total number of pixels, do not smooth to account for differences
    keys = list(range(1, 18))
    land_cover = {f"land_cover_{k:02d}": land_cover.get(str(k), 0) for k in keys}

    return dict(
        name=key,
        **population_density,
        **elevation,
        # map over values and convert to celsius
        **{k: t_modis_to_celsius(v) for k, v in surface_temp.items()},
        **land_cover,
    )


def main():
    """Run google earth engine to get elevation, temperature, and land cover data."""
    parser = ArgumentParser()
    parser.add_argument("region", type=str, choices=["ca", "western_us"])
    parser.add_argument("grid_size", type=int)
    parser.add_argument("output", type=str)
    parser.add_argument("--parallelism", type=int, default=8)
    args = parser.parse_args()

    ee.Initialize()

    if args.region == "ca":
        geometry = get_california_geometry()
        extent = CA_EXTENT
    elif args.region == "western_us":
        geometry = get_western_us_geometry()
        extent = WESTERN_US_EXTENT
    else:
        raise ValueError(f"Invalid region: {args.region}")

    grid = generate_grid(geometry, extent, (args.grid_size, args.grid_size))
    stats = []

    keys = list(grid.keys())

    with Pool(args.parallelism) as p:
        stats = list(
            tqdm(
                p.imap(partial(get_stats, grid), keys),
                total=len(keys),
            )
        )
    df = pd.DataFrame(stats)
    df.insert(1, "grid_size", args.grid_size)
    df.insert(1, "region", args.region)
    print(df.head())
    df.to_parquet(args.output)


if __name__ == "__main__":
    main()
