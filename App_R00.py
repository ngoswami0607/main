# main.py

import streamlit as st
from functions.building_dimension import building_dimension

st.set_page_config(page_title="Wind Load Calculator", layout="centered")

st.title("🌪️ Wind Load Calculator (ASCE 7)")
st.markdown("---")

# Step 1: Call your function
least_width, longest_width, height = building_dimension()

st.write(f"Returned values: {least_width} ft x {longest_width} ft x {height} ft")
