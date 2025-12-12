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
st.header("1️⃣ Building Dimensions")

col1, col2, col3 = st.columns(3)
least_width = col1.number_input("Least Width (ft)", min_value=0.0, value=30.0, format="%.2f")
longest_width = col2.number_input("Longest Width (ft)", min_value=0.0, value=80.0, format="%.2f")
height = col3.number_input("Mean Roof Height (ft)", min_value=0.0, value=30.0, format="%.2f")

least_width, longest_width, height = building_dimension()

# Step 2
location = code_jurisdiction_1()

# Step 3
risk_category = risk_category()

# Step 4
V = wind_speed(height,V)

# Step 5
wind_pressure_calc()

