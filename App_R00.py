import sys
import os
import streamlit as st
import traceback

from auth import authenticate_user
from functions.building_dimension import building_dimension
from functions.code_jurisdiction_1 import code_jurisdiction_1
from functions.risk_category import risk_category
from functions.wind_speed import wind_speed
from functions.wind_pressure_calc import wind_pressure_calc
from functions.roof_type_picker import roof_type_picker
from functions.internal_pressure import internal_pressure
from functions.h_less_than_60ft import show_h_less_than_60ft

authenticate_user()

# print(os.listdir("functions"))

#st.set_page_config(page_title="Wind Load Calculator", layout="wide")
st.set_page_config(page_title="Wind Load Calculator", layout="centered")
st.title("Wind Load Calculator (ASCE 7)")
st.markdown("This calculator helps you organize inputs for **ASCE 7 wind load determination**.")
st.markdown("---")

# Step 1 (ONLY here — remove the duplicate number_inputs you had in App_R00.py)
least_width, longest_width, height = building_dimension()

# Step 2: roof type picker (uses height)
roof_info = roof_type_picker(height)

# Step 3
jurisdiction = code_jurisdiction_1()

# Step 4
risk_category = risk_category()

# Step 5
V = wind_speed()

# Step 6
exposure, Kz, q = wind_pressure_calc(height, V)

# Step 7: Internal pressure classification
enclosure,gcpi_positive,gcpi_negative = internal_pressure()

# Step 8
if height < 60:

    show_h_less_than_60ft(
        height,
        q,
        gcpi_positive,
        gcpi_negative
    )

