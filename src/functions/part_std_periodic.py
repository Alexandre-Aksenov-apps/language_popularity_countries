import polars as pl
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


def part_std_periodic(ser: pl.Series) -> float:
    std_original = np.std(ser.to_numpy())
    decomposed = seasonal_decompose(ser, model="additive", period=12)

    std_seasonal = float(np.std(decomposed.seasonal))
    # Casting with 'float' is used
    # for seasonal_decompose does not declare its output type.

    ratio_seasonal = std_seasonal / std_original
    return ratio_seasonal
