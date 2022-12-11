import numpy as np
import pymc as pm

from birdcall_distribution.data import prepare_scaled_data
from birdcall_distribution.geo import get_modis_land_cover_name


def _scaled_data_old(prep_df):
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


def _scaled_data(prep_df):
    covariate_cols = prep_df.columns[5:-1]
    log_cols = [c for c in covariate_cols if "population" in c or "land_cover" in c]
    return prepare_scaled_data(prep_df, covariate_cols, log_cols, intercept=False)


def _coords(prep_df, scaled_data_df):
    species_cat = prep_df.primary_label.astype("category")
    snake_case = lambda s: s.replace(" ", "_").replace("/", "_").lower()
    norm = (
        lambda c: f"{c}_{snake_case(get_modis_land_cover_name(c))}"
        if "land_cover" in c
        else c
    )
    features = [norm(c) for c in scaled_data_df.columns.values]
    coords = dict(
        features_idx=features,
        species_idx=species_cat.cat.categories,
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
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
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
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
        # hyperpriors for intercept
        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Exponential("intercept_sigma", 1)
        intercept = pm.Normal(
            "intercept",
            mu=intercept_bar,
            sigma=np.sqrt(intercept_sigma),
            dims="species_idx",
        )
        mu = pm.Deterministic(
            "mu", pm.math.exp(intercept[species_idx] + phi[adj_idx]), dims="obs_idx"
        )
        pm.Poisson(
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
        )
    return model


def make_pooled_intercept_car_model(prep_df, W, *args, **kwargs):
    """Model intercept per species and CAR for spatial varying effects."""
    scaled_data_df = _scaled_data(prep_df)

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
        )

        alpha = pm.Beta("alpha", 5, 1)
        tau_phi = pm.Gamma("tau_phi", 1e-3, 1e-3)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=tau_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        intercept = pm.Normal("intercept", mu=0, tau=1e-4)
        mu = pm.Deterministic(
            "mu", pm.math.exp(intercept + phi[adj_idx]), dims="obs_idx"
        )
        pm.Poisson(
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(1e-6),
            dims="obs_idx",
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
        )
    return model


def make_pooled_intercept_varying_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
        )
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
            sigma=pm.math.sqrt(betas_sigma),
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
        )
    return model


def make_pooled_intercept_pooled_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
        )
        X = pm.ConstantData("X", scaled_data_df, dims=("obs_idx", "features_idx"))

        alpha = pm.Beta("alpha", 5, 1)
        tau_phi = pm.Gamma("tau_phi", 1, 1)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=tau_phi,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )

        # sum to zero constraint?
        # https://discourse.pymc.io/t/writing-tests-for-the-log-probability-of-the-sum-to-zero-icar-prior-via-pm-potential/10144/3
        # logp_func = pm.Normal.dist(mu=0.0, sigma=np.sqrt(0.001))
        # pm.Potential("zero_sum", pm.logp(logp_func, pm.math.sum(phi)))

        intercept = pm.Normal("intercept", mu=0, tau=1e-3)
        betas = pm.Normal("betas", mu=0, tau=1e-3, dims="features_idx")
        # print(pm.math.dot(X, betas).eval().shape)
        # print(phi[adj_idx].eval().shape)
        mu = pm.Deterministic(
            "mu",
            pm.math.exp(intercept + pm.math.sum(X * betas, axis=1) + phi[adj_idx]),
            dims="obs_idx",
        )
        # print(mu.eval().shape)
        pm.Poisson(
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(1e-3),
            dims="obs_idx",
        )
    return model


def make_varying_intercept_pooled_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
        )
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        alpha = pm.Beta("alpha", 5, 1)
        tau_phi = pm.Gamma("tau_phi", 1e-3, 1e-3)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=tau_phi,
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
            sigma=pm.math.sqrt(betas_sigma),
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
        )
    return model


def make_varying_intercept_varying_covariate_car_model(prep_df, W, *args, **kwargs):
    scaled_data_df = _scaled_data(prep_df)
    species_cat = prep_df.primary_label.astype("category")

    with pm.Model(coords=_coords(prep_df, scaled_data_df)) as model:
        species_idx = pm.ConstantData(
            "species_idx", species_cat.cat.codes, dims="obs_idx"
        )
        adj_idx = pm.ConstantData(
            "adj_idx", prep_df.index.values.astype(int), dims="obs_idx"
        )
        X = pm.ConstantData(
            "X", scaled_data_df.values, dims=("obs_idx", "features_idx")
        )

        alpha = pm.Beta("alpha", 5, 1)
        sigma_phi = pm.Uniform("sigma_phi", 0, 20)
        phi = pm.CAR(
            "phi",
            mu=np.zeros(W.shape[0]),
            tau=1 / sigma_phi**2,
            alpha=alpha,
            W=W,
            dims="adj_idx",
        )
        intercept_bar = pm.Normal("intercept_bar", mu=0, sigma=1.5)
        intercept_sigma = pm.Gamma("intercept_sigma", 1e-3, 1e-3)
        intercept = pm.Normal(
            "intercept",
            mu=intercept_bar,
            sigma=pm.math.sqrt(intercept_sigma),
            dims="species_idx",
        )
        betas_bar = pm.Normal("betas_bar", mu=0, sigma=1.5)
        betas_sigma = pm.Gamma("betas_sigma", 1e-3, 1e-3)
        betas = pm.Normal(
            "betas",
            mu=betas_bar,
            sigma=pm.math.sqrt(betas_sigma),
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
            "y",
            mu=mu,
            observed=np.ma.masked_invalid(prep_df.y.values).filled(0),
            dims="obs_idx",
        )
    return model
