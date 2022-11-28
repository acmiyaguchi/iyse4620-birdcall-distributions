# BirdCLEF Birdcall Distribution Maps

## Abstract

We utilize geo-spatial features of bird call metadata from the BirdCLEF 2022 competition to derive a distribution map for a subset of species in California and the Western United States.
We build several Bayesian models that incorporates species frequency information and remote sensing data from USGS and NASA in a regular lattice built from area-of-interest (AOI) geometries, using both hierarchical modeling to incorporate information across a subset of species and a conditional autoregressive (CAR) distribution for spatial random effects.
We generate several species distribution maps and make qualitative comparisons against known distribution maps.
All code and data is available on-request, and may be available publicly on Github/GCP pending permission from course instructors.

## Background

We are interested in whether we can produce and analyze species distribution map using Bayesian methods.

The BirdCLEF Challenge is a year competition held as part of the Conference and Labs of the Evaluation Forum.
The purpose of the challenge is to classify bird call segments and species from soundscapes captured from audio recording devices deployed in the fields.
The competition hosts provide a training dataset derived from xeno-canto, a crowd-sourced platform for sharing user-generated recordings of bird calls from around the world.

## Dataset

### BirdCLEF 2022 Training Metadata

The BirdCLEF 2022 competition provides TODO recordings from TODO species.
We are interested in the spatial features from the recording metadata, which are the latitude and longitude of the recording.
The recordings in the competition dataset are drawn from the xeno-canto library, but it does not reflect the entirety of the library.
Each species is capped to 500 recordings in the dataset, with frequency of recordings generally correlated with their rarity in nature and population density among other factors.

### Google Earth Engine

Google Earth Engine is a cloud-based platform for processing geospatial data.
We use Earth Engine to access remote sensing data from the United States Geological Survey (USGS) and the National Aeronautics and Space Administration (NASA).
We obtain elevation, temperature, land cover classification, and population density data from various sources hosted on Earth Engine.

Elevation data is derived from TODO.
Temperature data is derived from TODO.
Land cover classification data is derived from TODO.
Population density data is derived from TODO.

We generate a regular lattice of polygons from area-of-interest (AOI) geometries which are used to generate a dataset for a region at a particular fraction of a degree resolution.
We choose California and the Western United States as our AOI, due to familiarity with the region and diversity of geography and climate.
The dataset is generated over each polygon in the lattice and computing an aggregate statistic from each data source.

## Methodology

### Conditional Autoregressive Distribution

The likelihood for a conditional autoregression (CAR) distribution is given by the following equation:

$$
\begin{equation}
f(x|W, \alpha, \tau) =
    \frac{|T|^{1/2}}{(2\pi)^{k/2}}
    \exp \left\{
        -\frac{1}{2} (x - \mu)^\prime T^{-1} (x - \mu)
    \right\}
\end{equation}
$$

where

$$
\begin{equation}
\begin{aligned}
    T &= (\tau D (I-\alpha W))^{-1} \\
    D &= diag(\sum_{i} W_{ij})
\end{aligned}
\end{equation}
$$

This is a special form of the multivariate normal with with a covariance matrix that captures the adjacency structure of the neighborhood graph.

### Hierarchical Modeling

## Analysis

- Spatial random effects as a form of local smoothing
- Hierarchical modeling as a form of incorporating information across species
- Missing data imputation with distributional assumptions

## Discussion

## Conclusion
