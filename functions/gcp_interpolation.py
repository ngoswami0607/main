import math
import numpy as np


def interpolate_gcp(area, df, column):

    return float(
        np.interp(
            math.log10(area),
            math.log10(df["Area (sf)"]),
            df[column]
        )
    )
