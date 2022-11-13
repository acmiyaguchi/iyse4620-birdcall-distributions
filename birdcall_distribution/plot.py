import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np


def dataframe_color_getter(df, key_col, value_col, key):
    property = df[value_col]
    vmin = property.min()
    vmax = property.max()
    color_getter = lambda x: plt.get_cmap("viridis")(np.interp(x, [vmin, vmax], [0, 1]))
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
):
    xmin, xmax, ymin, ymax = map_dims

    # plot map with lattice of polygons
    fig = plt.figure(figsize=figsize)
    projection = ccrs.PlateCarree()
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

    if color_callback:
        cbar = fig.colorbar(plt.matplotlib.cm.ScalarMappable(norm=None, cmap="viridis"))
        cbar.set_ticks(np.linspace(0, 1, 6))
        cbar.set_ticklabels(
            [
                f"{round(np.interp(x, [0, 1], [vmin, vmax]), 2)}"
                for x in cbar.get_ticks()
            ]
        )
    ax.stock_img()
