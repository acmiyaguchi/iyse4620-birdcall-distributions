# Earth Engine Plots

We collected various statistics about each region using Google Earth Engine.
We incorporate the data into our models as covariates in a linear model, where we compute a posterior distribution for a regular lattice (i.e. grid) of cells.

We obtain population density, elevation, temperature, and land cover classification data for each grid cell.
The [NASA Shuttle Radar Topography Mission](https://lpdaac.usgs.gov/products/srtmgl1v003/) dataset ([`USGS/SRTMGL1_003`](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003)) provides elevation data.
The [MODIS/Terra Land Surface Temperature/Emissivity](https://modis.gsfc.nasa.gov/data/dataprod/mod11.php) dataset ([`MODIS/006/MOD11A1`](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A1)) provides temperature data.
The [MODIS/Terra Aqua Land Cover Type dataset](https://modis.gsfc.nasa.gov/data/dataprod/mod12.php) ([`MODIS/006/MCD12Q1`](https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MCD12Q1)) provides land cover classification statistics.
The [Gridded Population of the World, Version 4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4) dataset ([`CIESIN/GPWv411/GPW_Population_Density`](https://developers.google.com/earth-engine/datasets/catalog/CIESIN_GPWv411_GPW_Population_Density)) provides population density data.
