def calculate_pressure(q, gcp, gcpi_positive, gcpi_negative, sign):

    if sign=="positive":
        return q*(gcp-gcpi_negative)

    elif sign=="negative":
        return q*(gcp-gcpi_positive)
