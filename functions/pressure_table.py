import pandas as pd

from functions.pressure_calculation import calculate_pressure


def create_wall_pressure_table(
        q,
        gcpi_positive,
        gcpi_negative
):

    areas = [
        10,
        20,
        50,
        100,
        200,
        500,
        1000
    ]


    rows=[]


    for area in areas:

        from functions.wall_gcp_chart import wall_gcp


        positive,z4,z5 = wall_gcp(area)


        rows.append({

            "Effective Area (sf)": area,


            "Zone 4 Positive (psf)":
            calculate_pressure(
                q,
                positive,
                gcpi_positive,
                gcpi_negative,
                "positive"
            ),


            "Zone 4 Negative (psf)":
            calculate_pressure(
                q,
                z4,
                gcpi_positive,
                gcpi_negative,
                "negative"
            ),


            "Zone 5 Negative (psf)":
            calculate_pressure(
                q,
                z5,
                gcpi_positive,
                gcpi_negative,
                "negative"
            )

        })


    return pd.DataFrame(rows)
