import numpy as np
import pymc as pm

from birdcall_distribution.data import prepare_scaled_data


def _scaled_data(prep_df):
    landcover_cols = [f"land_cover_{i:02d}" for i in [7, 8, 9, 10, 16]]
    data_cols = [
        "population_density",
        "elevation_p50",
        "LST_Day_1km_p95",
        "LST_Night_1km_p5",
        *landcover_cols,
    ]
    scaled_data_df = prepare_scaled_data(
        prep_df, data_cols, ["population_density"] + landcover_cols, intercept=False
    )
    return scaled_data_df


def _coords(prep_df, scaled_data_df):
    species_cat = prep_df.primary_label.astype("category")
    n_features = scaled_data_df.shape[1]
    coords = dict(
        features_idx=np.arange(n_features),
        species_idx=sorted(species_cat.cat.codes.unique()),
        adj_idx=sorted(prep_df.index.unique()),
        obs_idx=np.arange(prep_df.shape[0]),
    )
    return coords


def make_varying_intercept_model(prep_df, *args, **kwargs):
    """Intercept-only model"""
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        intercept = pm.Normal("intercept", mu=0, tau=1e-4, dims="species_idx")
        mu = pm.Deterministic("mu", pm.math.exp(intercept[species_idx]), dims="obs_idx")
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )

    return model


def make_varying_intercept_car_model(prep_df, W, *args, **kwargs):
    """Model intercept per species and CAR for spatial varying effects."""
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData("adj_idx", prep_df.index.values, dims="obs_idx")

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        # hyperpriors for intercept
        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept", mu=intercept_bar, tau=1 / intercept_sigma, dims="species_idx"
        )
        mu = pm.Deterministic(
            "mu", pm.math.exp(intercept[species_idx] + phi[adj_idx]), dims="obs_idx"
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_pooled_intercept_car_model(prep_df, W, *args, **kwargs):
    """Model intercept per species and CAR for spatial varying effects."""
    scaled_data_df = _scaled_data(prep_df)

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        adj_idx = pm.ConstantData("adj_idx", prep_df.index.values, dims="obs_idx")

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        intercept = pm.Normal("intercept", mu=0, tau=1e-4)
        mu = pm.Deterministic(
            "mu", pm.math.exp(intercept + phi[adj_idx]), dims="obs_idx"
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_varying_intercept_pooled_covariate_model(prep_df, *args, **kwargs):
    """Model intercept per species and shared covariate"""
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept", mu=intercept_bar, tau=1 / intercept_sigma, dims="species_idx"
        )
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas", mu=betas_bar, tau=1 / betas_sigma, dims="features_idx"
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(intercept[species_idx] + pm.math.sum(X * betas, axis=1)),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_pooled_intercept_pooled_covariate_model(prep_df, *args, **kwargs):
    """Model intercept per species and shared covariate"""
    scaled_data_df = _scaled_data(prep_df)

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        intercept = pm.Normal("intercept", mu=0, tau=1e-4)
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas", mu=betas_bar, tau=1 / betas_sigma, dims="features_idx"
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(intercept + pm.math.sum(X * betas, axis=1)),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_pooled_intercept_varying_covariate_model(prep_df, *args, **kwargs):
    """Model intercept per species and shared covariate"""
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        intercept = pm.Normal("intercept", mu=0, tau=1e-4)
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            tau=1 / betas_sigma,
            dims=("species_idx", "features_idx"),
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(intercept + pm.math.sum(X * betas[species_idx], axis=1)),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_varying_intercept_varying_covariate_model(prep_df, *args, **kwargs):
    """Model intercept per species and shared covariate"""
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept", mu=intercept_bar, tau=1 / intercept_sigma, dims="species_idx"
        )
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            tau=1 / betas_sigma,
            dims=("species_idx", "features_idx"),
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(
                intercept[species_idx] + pm.math.sum(X * betas[species_idx], axis=1)
            ),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_pooled_intercept_varying_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData("adj_idx", prep_df.index.values, dims="obs_idx")
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        intercept = pm.Normal("intercept", mu=0, tau=1e-4)
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            tau=1 / betas_sigma,
            dims=("species_idx", "features_idx"),
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(
                intercept + pm.math.sum(X * betas[species_idx], axis=1) + phi[adj_idx]
            ),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_varying_intercept_pooled_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData("adj_idx", prep_df.index.values, dims="obs_idx")
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )

        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept", mu=intercept_bar, tau=1 / intercept_sigma, dims="species_idx"
        )
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            tau=1 / betas_sigma,
            dims="features_idx",
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(
                intercept[species_idx] + pm.math.sum(X * betas, axis=1) + phi[adj_idx]
            ),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model


def make_varying_intercept_varying_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData("adj_idx", prep_df.index.values, dims="obs_idx")
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept", mu=intercept_bar, tau=1 / intercept_sigma, dims="species_idx"
        )
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Exponential("betas_sigma", 1)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            tau=1 / betas_sigma,
            dims=("species_idx", "features_idx"),
        )
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(
                intercept[species_idx]
                + pm.math.sum(X * betas[species_idx], axis=1)
                + phi[adj_idx]
            ),
            dims="obs_idx",
        )
        pm.Poisson(
            "y", mu=mu, observed=np.ma.masked_invalid(prep_df.y.values), dims="obs_idx"
        )
    return model
