# bircall-distribution

To get statistics about elevation, temperature, and land cover classification:

```bash
python -m birdcall_distribution.commands.earth_engine data/earth_engine.parquet
```

## datasets

- https://esa-worldcover.org/en/data-access
- https://worldcover2020.esa.int/
- https://cloud.google.com/storage/docs/public-datasets/landsat

- https://gis.stackexchange.com/questions/419979/calculating-pixel-area-in-region-using-esa-worldcover-10-m-v100-in-google-earth
- https://spatialthoughts.com/2020/06/19/calculating-area-gee/

- https://modis.gsfc.nasa.gov/data/dataprod/mod12.php
- https://gis.stackexchange.com/questions/407240/code-for-generating-tiles-grids-on-google-earth-engine
- https://developers.google.com/earth-engine/tutorials/community/drawing-tools
- https://gis.stackexchange.com/questions/388608/reduceregions-google-earth-engine-python-api

- https://github.com/pangeo-data/cog-best-practices/blob/main/2-dask-localcluster.ipynb

## modeling geospatial data

- https://www.pymc-labs.io/blog-posts/spatial-gaussian-process-01/
  - writes a custom covariance kernel that does chordal distance to any points on a sphere
- https://docs.pymc.io/en/v3/pymc-examples/examples/case_studies/conditional-autoregressive-model.html
  - CAR model for smoothing
- https://www.mdpi.com/2075-1680/10/4/307
- https://atlas.cancer.org.au/developing-a-cancer-atlas/Chapter_4.html
  - overview of spatial models
- https://uoftcoders.github.io/studyGroup/lessons/python/cartography/lesson/
  - cartography stuff
- https://sedac.ciesin.columbia.edu/data/collection/gpw-v4
  - population data
- https://www.ism.ac.jp/editsec/aism/pdf/10463_2010_Article_298.pdf
  - CAR model
- https://mc-stan.org/users/documentation/case-studies/mbjoseph-CARStan.html
  - CAR in STAN
- https://timeseriesreasoning.com/contents/exogenous-and-endogenous-variables/
  - exogenous variables in a model?
- https://oriolabrilpla.cat/python/arviz/pymc3/xarray/2020/09/22/pymc3-arviz.html
  - dealing with coords in pymc
- https://stats.stackexchange.com/questions/561263/poisson-or-binomial-distribution-for-modeling
  - binomial or poisson?
- https://onlinelibrary.wiley.com/doi/full/10.1111/ecog.06022
  - bernoulli?
- https://www.nature.com/articles/s41598-019-49549-4
  - spatial random effects with icar
- http://stronginference.com/missing-data-imputation.html

## temperature and landcover

- https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api
- https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MCD12Q1#bands
- https://gis.stackexchange.com/questions/304929/what-is-the-difference-between-sample-sampleregions-and-stratifiedsample-in-go
