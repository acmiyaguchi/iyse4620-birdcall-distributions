from functools import partial

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

from .geo import get_grid_meta

COLORMAP = "viridis"


def dataframe_color_getter(df, key_col, value_col, key):
    property = df[value_col]
    vmin = property.min()
    vmax = property.max()
    color_getter = lambda x: plt.get_cmap(COLORMAP)(np.interp(x, [vmin, vmax], [0, 1]))
    try:
        return color_getter(df[df[key_col] == key][value_col].values[0])
    except IndexError:
        return (1, 1, 1, 0)


def plot_lonlat_points(geometry, map_dims, df):
    xmin, xmax, ymin, ymax = map_dims

    # plot map with lattice of polygons
    fig = plt.figure(figsize=(12, 7))
    projection = ccrs.PlateCarree()
    ax = plt.axes(projection=projection)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    ax.add_feature(
        cfeature.ShapelyFeature([geometry], projection),
        edgecolor="k",
        facecolor=(1, 1, 1, 0),
    )

    ax.scatter(df["longitude"], df["latitude"], transform=ccrs.PlateCarree())
    ax.stock_img()


def plot_grid(
    geometry,
    map_dims,
    grid,
    color_callback=None,
    vmin=None,
    vmax=None,
    draw_gridline=True,
    figsize=(12, 7),
    ax=None,
    projection=None,
    colorbar=True,
):
    xmin, xmax, ymin, ymax = map_dims

    # plot map with lattice of polygons
    if not projection:
        projection = ccrs.PlateCarree()
    if ax is None:
        plt.figure(figsize=figsize)
        ax = plt.axes(projection=projection)

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    if draw_gridline:
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    for key, polygon in grid.items():
        ax.add_feature(
            cfeature.ShapelyFeature([polygon], projection),
            edgecolor="gray",
            facecolor=color_callback(key) if color_callback else (1, 1, 1, 0),
        )

    ax.add_feature(
        cfeature.ShapelyFeature([geometry], projection),
        edgecolor="k",
        facecolor=(1, 1, 1, 0),
    )

    if color_callback and colorbar:
        # some magic numbers for scaling: https://stackoverflow.com/a/26720422
        cbar = plt.colorbar(
            plt.matplotlib.cm.ScalarMappable(norm=None, cmap=COLORMAP),
            fraction=0.04,
            pad=0.04,
            ax=ax,
        )
        cbar.set_ticks(np.linspace(0, 1, 6))
        cbar.set_ticklabels(
            [
                f"{round(np.interp(x, [0, 1], [vmin, vmax]), 2)}"
                for x in cbar.get_ticks()
            ]
        )
    ax.stock_img()


def plot_species(df, species, prop="y", ax=None, title=None, **kwargs):
    """Used to plot the distribution of a species in a dataset"""
    sub_df = df[df.primary_label == species]
    region = sub_df.region.values[0]
    grid_size = sub_df.grid_size.values[0]
    grid_meta = get_grid_meta(region, grid_size)

    # note that we use a shared colorbar
    plot_grid(
        grid_meta.geometry,
        grid_meta.extent,
        grid_meta.grid,
        color_callback=partial(dataframe_color_getter, sub_df, "grid_id", prop),
        vmin=df[prop].min(),
        vmax=df[prop].max(),
        draw_gridline=False,
        figsize=(5, 7),
        ax=ax,
        **kwargs,
    )
    if not title:
        title = f"Birdcall Recording Frequency for {species}"
    if ax is None:
        ax = plt.gca()
    ax.set_title(title)


def plot_species_subplot(
    df, species_list, prop="y", species_mapper={}, subtitle=None, **kwargs
):
    # create a subplot in a 2x2 grid
    fig, axs = plt.subplots(
        2, 2, figsize=(9, 7), subplot_kw={"projection": ccrs.PlateCarree()}
    )
    axes = axs.flatten()
    for i, species in enumerate(species_list):
        common = species_mapper.get(species)
        count = df[df.primary_label == species][prop].sum()
        plot_species(
            df,
            species,
            ax=axes[i],
            colorbar=False,
            title=(
                f"{common} ({species}, n={count})"
                if common
                else f"{species}, n={count}"
            ),
            **kwargs,
        )

    # https://stackoverflow.com/questions/8248467/tight-layout-doesnt-take-into-account-figure-suptitle
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    vmin = df[prop].min()
    vmax = df[prop].max()

    # https://stackoverflow.com/questions/13784201/how-to-have-one-colorbar-for-all-subplots
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.83, 0.10, 0.03, 0.8])
    cbar = fig.colorbar(
        plt.matplotlib.cm.ScalarMappable(norm=None, cmap=COLORMAP),
        fraction=0.04,
        pad=0.04,
        cax=cbar_ax,
    )
    cbar.set_ticks(np.linspace(0, 1, 6))
    cbar.set_ticklabels(
        [f"{round(np.interp(x, [0, 1], [vmin, vmax]), 2)}" for x in cbar.get_ticks()]
    )
    title = "Birdcall Recording Frequency"
    if subtitle:
        title += f" ({subtitle})"
    fig.suptitle(title)


def plot_ppc_species(prep_df, ppc, species, prop="log_pred", ax=None):
    pred_df = prep_df.copy()
    shape = prep_df.shape
    pred_df["pred"] = ppc.posterior_predictive.y.values.reshape(-1, shape[0]).mean(
        axis=0
    )
    pred_df["log_pred"] = np.log(pred_df.pred)
    pred_df = pred_df[prep_df.primary_label == species]

    plt.figure(figsize=(5, 3))
    plt.hist(pred_df[prop], bins=20)
    plt.title(f"histogram of {prop} for {species}")
    plt.show()

    region = pred_df.region.values[0]
    grid_size = pred_df.grid_size.values[0]
    grid_meta = get_grid_meta(region, grid_size)

    # plot the posterior predictive
    plot_grid(
        grid_meta.geometry,
        grid_meta.extent,
        grid_meta.grid,
        color_callback=partial(dataframe_color_getter, pred_df, "grid_id", prop),
        vmin=pred_df[prop].min(),
        vmax=pred_df[prop].max(),
        draw_gridline=False,
        figsize=(5, 7),
        ax=ax,
    )
    plt.title(f"Birdcall Recording Frequency prediction for {species}")
