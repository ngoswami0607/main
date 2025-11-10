import sys, os
import streamlit as st

# Import each functional block
from functions.building_dimension import building_dimension
from functions.code_jurisdiction_1 import code_jurisdiction_1
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

if st.button("🔍 Fetch ICC Code Information"):
    with st.spinner(f"Fetching ICC codes for {location}..."):
        if location.strip():
            result = fetch_icc_codes(location)
            st.markdown("### 📘 Applicable Building Codes:")
            st.markdown(result)
        else:
            st.warning("Please enter a valid location name.")

# Step 3
risk_category = risk_category()

# Step 4
V = wind_speed()

# Step 5
wind_pressure_calc(height, V)

