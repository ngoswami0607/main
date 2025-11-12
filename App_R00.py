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

authenticate_user()

# print(os.listdir("functions"))

st.set_page_config(page_title="Wind Load Calculator", layout="centered")
st.title("🌪️ Wind Load Calculator (ASCE 7)")

st.markdown("""
This calculator helps you organize inputs for **ASCE 7 wind load determination**.
""")
st.markdown("---")

# Step 1
least_width, longest_width, height = building_dimension()

# Step 2
location = code_jurisdiction_1()

# Step 3
risk_category = risk_category()

# Step 4
V = wind_speed(height,V)

# Step 5
wind_pressure_calc()

