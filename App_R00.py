import sys, os
import streamlit as st

# Import each functional block
from functions.building_dimension import building_dimension
from functions.code_jurisdiction import code_jurisdiction
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
asce_code = code_jurisdiction()

# Step 3
risk_category = risk_category()

# Step 4
V = wind_speed()

# Step 5
wind_pressure_calc(height, V)

