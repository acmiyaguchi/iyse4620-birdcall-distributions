We split each region into a grid and summarize birdcall recording observations into each grid cell.
The grids are defined in degrees of latitude or longitude.
These discrete cells help when fitting a Bayesian model to the data, and also allow us to incorporate external geographical information derived from Google Earth Engine.
The cells are small enough to be computationally tractable, but large enough to capture the spatial variation in the data.

The posterior predictive is the estimated point prediction for the number of observations in each grid cell, derived from the posterior distribution of the model parameters.
