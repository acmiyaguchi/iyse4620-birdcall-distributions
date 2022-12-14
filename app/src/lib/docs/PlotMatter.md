We split each region into a grid (or regular lattice) and summarized birdcall recording observations into each grid cell.
We define the grid in degrees of latitude or longitude.
These discrete cells help fit a Bayesian model to the data and allow us to incorporate external geographical information derived from Google Earth Engine.
The cells are small enough to be computationally tractable but large enough to capture the spatial variation in the data.
See the [Earth Engine Plots](./earth-engine) page for more information about the data we use from Google Earth Engine.

The [posterior predictive](https://en.wikipedia.org/wiki/Posterior_predictive_distribution) is the estimated point prediction for the number of observations in each grid cell derived from the posterior distribution of the model parameters.
