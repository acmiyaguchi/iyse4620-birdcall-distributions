import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from birdcall_distribution.geo import (
    add_lonlat_columns,
    convert_to_adjacency_matrix,
    generate_grid_adjacency_list,
    get_adjacency_mapping,
    get_grid_meta,
)


def prepare_dataframe(ee_path, train_path, n_species=3):
    """Prepare dataframe and adjacency matrix for fitting"""

    # dataset with our data from earth engine
    ee_df = pd.read_parquet(ee_path)
    grid_size = ee_df.grid_size.values[0]
    region = ee_df.region.values[0]

    grid_meta = get_grid_meta(region, grid_size)

    adjacency_list = generate_grid_adjacency_list(grid_meta.grid)
    mapping = get_adjacency_mapping(adjacency_list)
    W = convert_to_adjacency_matrix(adjacency_list)

    # pull out species and longitude/latitude data from the kaggle dataset
    df = pd.read_csv(train_path)
    df = df[["primary_label", "latitude", "longitude"]].dropna()
    df = add_lonlat_columns(df, grid_meta.grid)
    df = df[df.grid.notnull()]
    df["adjacency_idx"] = df.grid_id.apply(lambda x: mapping.get(x, None))

    # now modify the species list so we only keep the top n
    if n_species:
        top_n = (
            df[["primary_label"]]
            .groupby("primary_label")
            .value_counts()
            .sort_values(ascending=False)[:n_species]
        )
        df["primary_label"] = df.primary_label.apply(
            lambda x: x if x in top_n.index else "other"
        )

    # count number of observed calls per adjacency index, and join against the ee variables
    group_cols = ["primary_label", "grid_id"]
    counts_df = df[group_cols].groupby(group_cols).value_counts().reset_index()
    counts_df.columns = group_cols + ["y"]

    ee_with_species = ee_df.rename(columns={"name": "grid_id"}).merge(
        pd.DataFrame({"primary_label": df.primary_label.unique()}), how="cross"
    )
    prep_df = counts_df.merge(
        ee_with_species, on=["grid_id", "primary_label"], how="outer"
    )
    prep_df["adjacency_idx"] = prep_df.grid_id.apply(lambda x: mapping.get(x, None))
    prep_df = prep_df.set_index("adjacency_idx").sort_index()

    landcover_cols = [c for c in prep_df.columns if c.startswith("land_cover")]
    prep_df["sum_land_cover"] = prep_df[landcover_cols].sum(axis="columns")

    return prep_df, W


def prepare_scaled_data(
    df, data_cols, log_cols=[], intercept=True, return_scaler=False
):
    scaler = StandardScaler()
    temp_df = df[data_cols].copy()

    if intercept:
        # add an intercept to the data cols
        temp_df["intercept"] = 1
        data_cols = ["intercept"] + data_cols

    for col in log_cols:
        temp_df[col] = np.log(temp_df[col] + 1)
    scaler.fit(temp_df)
    scaled_data_df = pd.DataFrame(scaler.transform(temp_df), columns=data_cols)

    if return_scaler:
        return scaled_data_df, scaler
    else:
        return scaled_data_df
