import json
from argparse import ArgumentParser
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm

from birdcall_distribution.geo import get_grid_meta, get_modis_land_cover_name
from birdcall_distribution.plot import dataframe_color_getter, plot_grid


def parse_args():
    """Parse args for the input and output paths"""
    parser = ArgumentParser()
    parser.add_argument("input", type=str, help="Path to the input dataset")
    parser.add_argument("output", type=str, help="Path to the output directory")
    return parser.parse_args()


def plot_features(df, output_path):
    """Plot all of the numerical features of the dataset using the plot_species function."""
    region = df.region.unique()[0]
    grid_size = df.grid_size.unique()[0]
    grid_meta = get_grid_meta(region, grid_size)

    props = df.columns[3:]

    for prop in tqdm.tqdm(props):
        plot_grid(
            grid_meta.geometry,
            grid_meta.extent,
            grid_meta.grid,
            color_callback=partial(dataframe_color_getter, df, "name", prop),
            vmin=df[prop].min(),
            vmax=df[prop].max(),
            draw_gridline=False,
            figsize=(5, 4.5),
        )
        name = (
            f"{prop}: {get_modis_land_cover_name(prop)}"
            if "land_cover" in prop
            else prop
        )
        plt.tight_layout()
        plt.title(name)
        plt.savefig(f"{output_path}/{prop}.png")
        plt.close()

    # plot log scaled
    for prop in tqdm.tqdm(props):
        df["log_" + prop] = df[prop].apply(lambda x: np.log(x + 1))
        prop = "log_" + prop
        plot_grid(
            grid_meta.geometry,
            grid_meta.extent,
            grid_meta.grid,
            color_callback=partial(dataframe_color_getter, df, "name", prop),
            vmin=df[prop].min(),
            vmax=df[prop].max(),
            draw_gridline=False,
            figsize=(5, 4.5),
        )
        name = (
            f"log {prop}: {get_modis_land_cover_name(prop)}"
            if "land_cover" in prop
            else prop
        )
        plt.tight_layout()
        plt.title(name)
        plt.savefig(f"{output_path}/{prop}.png")
        plt.close()

    return props


def main():
    args = parse_args()
    input_path = Path(args.input)

    # search for all parquet datasets that contain v3 in them
    parquet_files = list(input_path.glob("*.parquet"))
    parquet_files = [f for f in parquet_files if "v3" in f.name]

    maps = []
    props = []
    # generate a plot for each of the features
    for parquet_file in list(reversed(parquet_files)):
        df = pd.read_parquet(parquet_file)
        region = df.region.unique()[0]
        grid_size = int(df.grid_size.unique()[0])
        maps.append(dict(region=region, grid_size=grid_size))
        output_path = Path(args.output) / f"{region}_{grid_size}"
        output_path.mkdir(exist_ok=True, parents=True)
        print("Plotting features for", parquet_file)
        props = plot_features(df, output_path)

    # output a manifest
    (
        (Path(args.output) / "manifest.json").write_text(
            json.dumps(dict(maps=maps, feature_names=list(props)), indent=2)
        )
    )


if __name__ == "__main__":
    main()
