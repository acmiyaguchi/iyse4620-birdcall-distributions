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


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    taxonomy_df = pd.read_csv(
        "https://storage.googleapis.com/birdclef-eda-f22/data/raw/birdclef-2022/eBird_Taxonomy_v2021.csv"
    )
    taxonomy_df.columns = taxonomy_df.columns.str.lower()
    species_mapper = taxonomy_df.set_index("species_code")["primary_com_name"].to_dict()

    # read manifest file
    with open(input_path / "manifest.json") as f:
        manifest = json.load(f)

    # get all the set of all species
    species = set([row["primary_label"] for row in manifest])
    mapper_subset = {k: v for k, v in species_mapper.items() if k in species}
    with open(output_path / "species_mapping.json", "w") as f:
        json.dump(mapper_subset, f, indent=2)


if __name__ == "__main__":
    main()
