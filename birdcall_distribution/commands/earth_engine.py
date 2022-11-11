from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool

import ee
import pandas as pd
from shapely.geometry import mapping
from tqdm.auto import tqdm

from birdcall_distribution.geo import CA_EXTENT, generate_grid, get_shape_us_state


def t_modis_to_celsius(t_modis):
    """Converts MODIS LST units to degrees Celsius."""
    if t_modis is None:
        return None
    t_celsius = 0.02 * t_modis - 273.15
    return t_celsius


def get_stats(grid, key, start_ds="2019-01-01", end_ds="2022-01-01", scale=1000):
    """Get statistics for elevation, temperature, and land cover."""
    geojson = mapping(grid[key])
    poi = ee.Geometry.Polygon(geojson["coordinates"])

    # Import the USGS ground elevation image.
    elevation = (
        ee.Image("USGS/SRTMGL1_003")
        .sample(poi, scale)
        .aggregate_stats("elevation")
        .getInfo()
    )

    # Import the MODIS land surface temperature collection.
    # temperature day and night, with quality control bands
    # we need to filter it first
    surface_temp = (
        ee.ImageCollection("MODIS/006/MOD11A1")
        .select("LST_Day_1km", "LST_Night_1km", "QC_Day", "QC_Night")
        .filterDate(start_ds, end_ds)
        .mean()
        .sample(poi, scale=scale)
    )

    surface_temp_day = surface_temp.aggregate_stats("LST_Day_1km").getInfo()
    surface_temp_night = surface_temp.aggregate_stats("LST_Night_1km").getInfo()

    # Import the MODIS land cover collection.
    land_cover = (
        ee.ImageCollection("MODIS/006/MCD12Q1")
        .first()
        .sample(poi, scale)
        .aggregate_histogram("LC_Type1")
        .getInfo()
    )

    # count the total number of pixels, and also normalize the values of the
    # scores knowing the set of keys ahead of time and we use laplace smoothing
    # to avoid zero counts
    total_pixels = sum(land_cover.values())
    keys = list(range(1, 18))
    land_cover = {
        f"land_cover_{k:02d}": (land_cover.get(str(k), 0) + 1)
        / (total_pixels + len(keys))
        for k in keys
    }

    return dict(
        name=key,
        total_pixels=total_pixels,
        elevation_mean=elevation["mean"],
        elevation_min=elevation["min"],
        elevation_max=elevation["max"],
        day_temp_mean=t_modis_to_celsius(surface_temp_day["mean"]),
        day_temp_min=t_modis_to_celsius(surface_temp_day["min"]),
        day_temp_max=t_modis_to_celsius(surface_temp_day["max"]),
        night_temp_mean=t_modis_to_celsius(surface_temp_night["mean"]),
        night_temp_min=t_modis_to_celsius(surface_temp_night["min"]),
        night_temp_max=t_modis_to_celsius(surface_temp_night["max"]),
        **land_cover,
    )


def main():
    """Run google earth engine to get elevation, temperature, and land cover data."""
    parser = ArgumentParser()
    parser.add_argument("output", type=str)
    parser.add_argument("--parallelism", type=int, default=8)
    args = parser.parse_args()

    ee.Initialize()

    ca_shape = get_shape_us_state("California")
    grid = generate_grid(ca_shape, CA_EXTENT, (0.25, 0.25))
    stats = []

    keys = list(grid.keys())

    with Pool(8) as p:
        stats = list(
            tqdm(
                p.imap(partial(get_stats, grid), keys),
                total=len(keys),
            )
        )
    df = pd.DataFrame(stats)
    print(df.head())
    df.to_parquet(args.output)


if __name__ == "__main__":
    main()
