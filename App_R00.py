import sys, os
import streamlit as st
import traceback

# Import each functional block
from functions.building_dimension import building_dimension
try:
    from functions.code_jurisdiction_1 import code_jurisdiction_1
except Exception:
    st.error("Import of functions.code_jurisdiction_1 failed — full traceback below.")
    st.code(traceback.format_exc())
    st.stop()

from functions.risk_category import risk_category
from functions.wind_speed import wind_speed
from functions.wind_pressure_calc import wind_pressure_calc

st.set_page_config(page_title="Wind Load Calculator", layout="centered")
st.title("🌪️ Wind Load Calculator (ASCE 7)")

st.markdown("""
This calculator helps you organize inputs for **ASCE 7 wind load determination**.
""")
st.markdown("---")

# Step 1
least_width, longest_width, height = building_dimension()

# Step 2
# asce_code = code_jurisdiction()
location = code_jurisdiction_1()

# Step 3
risk_category = risk_category()

# Step 4
V = wind_speed()

# Step 5
wind_pressure_calc(height, V)

