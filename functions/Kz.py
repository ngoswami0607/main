def compute_kz(height_ft: float, exposure: str) -> float:
    """
    Returns Kz using ASCE 7-16 Table 26.10-1 with linear interpolation.

    Parameters
    ----------
    height_ft : float
        Mean roof height (ft)
    exposure : str
        Exposure category: "B", "C", or "D"

    Returns
    -------
    float
        Velocity pressure exposure coefficient Kz
    """

    table = {
        "B": {
            15: 0.57, 20: 0.62, 25: 0.66, 30: 0.70, 40: 0.76, 50: 0.81,
            60: 0.85, 70: 0.89, 80: 0.93, 90: 0.96, 100: 0.99,
            120: 1.04, 140: 1.09, 160: 1.13, 200: 1.20,
            250: 1.28, 300: 1.35, 350: 1.41, 400: 1.47,
            450: 1.52, 500: 1.56,
        },
        "C": {
            15: 0.85, 20: 0.90, 25: 0.94, 30: 0.98, 40: 1.04, 50: 1.09,
            60: 1.13, 70: 1.17, 80: 1.21, 90: 1.24, 100: 1.26,
            120: 1.31, 140: 1.36, 160: 1.39, 200: 1.46,
            250: 1.53, 300: 1.59, 350: 1.64, 400: 1.69,
            450: 1.73, 500: 1.77,
        },
        "D": {
            15: 1.03, 20: 1.08, 25: 1.12, 30: 1.16, 40: 1.22, 50: 1.27,
            60: 1.31, 70: 1.34, 80: 1.38, 90: 1.40, 100: 1.43,
            120: 1.48, 140: 1.52, 160: 1.55, 200: 1.61,
            250: 1.68, 300: 1.73, 350: 1.78, 400: 1.82,
            450: 1.86, 500: 1.89,
        },
    }

    # Clamp height to table limits
    h = max(15.0, min(float(height_ft), 500.0))
    heights = sorted(table[exposure].keys())

    # Linear interpolation
    for i in range(len(heights) - 1):
        h1, h2 = heights[i], heights[i + 1]
        if h1 <= h <= h2:
            k1 = table[exposure][h1]
            k2 = table[exposure][h2]
            return k1 + (k2 - k1) * (h - h1) / (h2 - h1)

    return table[exposure][500]
