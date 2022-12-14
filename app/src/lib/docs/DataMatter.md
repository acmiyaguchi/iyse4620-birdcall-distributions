Data for this project can be found in the `gs://iyse6420-birdcall-distribution` bucket.
Here are the direct links to source data:

- [raw/birdclef-2022/train_metadata.csv](https://storage.googleapis.com/iyse6420-birdcall-distribution/raw/birdclef-2022/train_metadata.csv)
- [ee_v3_ca_1.parquet](https://storage.googleapis.com/iyse6420-birdcall-distribution/ee_v3_ca_1.parquet)
- [ee_v3_western_us_2.parquet](https://storage.googleapis.com/iyse6420-birdcall-distribution/ee_v3_western_us_2.parquet)
- [ee_v3_americas_5.parquet](https://storage.googleapis.com/iyse6420-birdcall-distribution/ee_v3_americas_5.parquet)
- [ee_v3_americas_2.parquet](https://storage.googleapis.com/iyse6420-birdcall-distribution/ee_v3_americas_2.parquet)

You can load this data directly into a Python session using `pandas` and `pyarrow`:

<div class="overflow-container">

```python
>>> import pandas as pd
>>> df = pd.read_parquet("https://storage.googleapis.com/iyse6420-birdcall-distribution/ee_v3_ca_1.parquet")
>>> df.head()
      name region  grid_size  population_density  ...  land_cover_14  land_cover_15  land_cover_16  land_cover_17
0  -125_39     ca          1            7.639377  ...              0              0              0            117
1  -125_40     ca          1       172360.641191  ...              0              0              2           1032
2  -125_41     ca          1        48910.677999  ...              0              0              0           1386
3  -125_42     ca          1        39462.664024  ...              0              0              0           1436
4  -124_38     ca          1        32485.186359  ...              0              0              3           1348

[5 rows x 30 columns]
>>> df.shape
(68, 30)
```

</div>

<style>
    .overflow-container {
        overflow-x: auto;
    }
</style>
