def calculate_pressure(q, gcp, gcpi_positive, gcpi_negative, sign):

    if sign=="positive":
        return 0.6*q*(gcp-gcpi_negative)

    elif sign=="negative":
        return 0.6*q*(gcp-gcpi_positive)
