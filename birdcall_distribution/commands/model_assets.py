from argparse import ArgumentParser
from functools import partial
from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc as pm
import tqdm

from birdcall_distribution import model
from birdcall_distribution.data import prepare_dataframe
from birdcall_distribution.plot import plot_ppc_species, plot_species


def generate_assets(model_type, df, W, output_path, species, cores=4, samples=1000):
    """Generate assets for a given species"""
    path = Path(output_path) / species
    path.mkdir(parents=True, exist_ok=True)

    # plot the data
    sub_df = df[df.primary_label == species].copy().fillna(0)

    model_func = {
        "intercept_car": model.make_pooled_intercept_car_model,
        "intercept_covariate_car": model.make_pooled_intercept_pooled_covariate_car_model,
    }[model_type]

    with model_func(sub_df, W):
        trace = pm.sample(samples, cores=cores)
        ppc = pm.sample_posterior_predictive(trace)

    # also save the trace
    summary = az.summary(trace, kind="stats", hdi_prob=0.95)
    summary.reset_index().to_json(
        f"{path}/trace_{species}.json",
        orient="records",
    )

    # save y and pred
    sub_df["pred"] = ppc.posterior_predictive.y.values.reshape(
        -1, sub_df.shape[0]
    ).mean(axis=0)
    sub_df["log_pred"] = np.log(sub_df.pred + 1)
    sub_df[
        ["primary_label", "grid_id", "region", "grid_size", "y", "pred", "log_pred"]
    ].to_json(f"{path}/ppc_{species}.json", orient="records")

    # try to use a consistent color scaling across plots of the same species
    vmin = 0
    vmax = max(sub_df.y.max(), sub_df.pred.max()) * 1.1

    figsize = (5, 5)
    plot_species(
        df, species, title=f"observed, {species}", vmin=vmin, vmax=vmax, figsize=figsize
    )
    plt.tight_layout()
    plt.savefig(f"{path}/observed_{species}.png")

    plot_ppc_species(
        sub_df,
        ppc,
        species,
        prop="log_pred",
        title=f"posterior predictive, {species}, log scale",
        vmin=np.log(vmin + 1),
        vmax=np.log(vmax),
        figsize=figsize,
    )
    plt.tight_layout()
    plt.savefig(f"{path}/ppc_{species}_log.png")

    plot_ppc_species(
        sub_df,
        ppc,
        species,
        prop="pred",
        title=f"posterior predictive, {species}, linear scale",
        vmin=vmin,
        vmax=vmax,
        figsize=figsize,
    )
    plt.tight_layout()
    plt.savefig(f"{path}/ppc_{species}_linear.png")


def parse_args():
    """Arguments for the input dataset, train metadata, output path, and pymc parameters"""
    parser = ArgumentParser()
    parser.add_argument(
        "model",
        type=str,
        choices=["intercept_car", "intercept_covariate_car"],
        help="Model to use for pymc sampling",
    )
    parser.add_argument("input", type=str, help="Path to the input dataset")
    parser.add_argument("output", type=str, help="Path to the output directory")
    parser.add_argument(
        "--train_metadata",
        type=str,
        default="data/raw/birdclef-2022/train_metadata.csv",
        help="Path to the train metadata",
    )
    parser.add_argument(
        "--n-species",
        type=int,
        default=10,
        help="Number of species to use for pymc sampling",
    )
    parser.add_argument(
        "--cores", type=int, default=4, help="Number of cores to use for pymc sampling"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=1000,
        help="Number of samples to use for pymc sampling",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    prep_df, W = prepare_dataframe(args.input, args.train_metadata, n_species=None)
    prep_df = prep_df[prep_df.index.notnull()]

    # get the top n species
    top_species = (
        prep_df.groupby("primary_label")
        .count()
        .y.sort_values(ascending=False)
        .head(args.n_species)
        .index
    )
    print(top_species)

    func = partial(
        generate_assets,
        args.model,
        prep_df,
        W,
        args.output,
        cores=args.cores,
        samples=args.samples,
    )
    for species in tqdm.tqdm(top_species):
        func(species=species)


if __name__ == "__main__":
    main()
