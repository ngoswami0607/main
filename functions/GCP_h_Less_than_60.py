import pandas as pd


def get_wall_gcp_data():

    areas = [1, 10,20,50,100,200,500,1000]

    return pd.DataFrame({

        "Area (sf)": areas,

        "Zone 4 Negative":
        [-1.1, -1.1, -1.046838103, -0.976561897, -0.9234, -0.870238103, -0.799961897, -0.8],

        "Zone 5 Negative":
        [-1.4, -1.4, -1.293676206, -1.153123794, -1.0468, -0.940476206, -0.799923794, -0.8],

        "Zones 4&5 Positive":
        [1.00, 1.00, 0.95, 0.88, 0.82, 0.77, 0.70, 0.70]

    })


def get_roof_gcp_data():

    areas = [10,20,50,100,200,500,1000]

    return pd.DataFrame({

        "Area (sf)": areas,

        "Zone 1 Negative":
        [-1.6,-1.6,-1.45,-1.35,-1.25,-1.0,-1.0],

        "Zone 2 Negative":
        [-2.3,-2.3,-2.1,-1.9,-1.7,-1.4,-1.4],

        "Zone 3 Negative":
        [-3.2,-3.2,-2.7,-2.4,-2.1,-1.4,-1.4],

        "Zone 1 Positive":
        [0.9,0.9,0.85,0.75,0.60,0.40,0.40]

    })
