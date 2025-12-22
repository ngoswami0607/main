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

authenticate_user()

# print(os.listdir("functions"))

st.set_page_config(page_title="Wind Load Calculator", layout="centered")
st.title("🌪️ Wind Load Calculator (ASCE 7)")
st.markdown("This calculator helps you organize inputs for **ASCE 7 wind load determination**.")
st.markdown("---")

# Step 1 (ONLY here — remove the duplicate number_inputs you had in App_R00.py)
least_width, longest_width, height = building_dimension()

# Step 2: roof type picker (uses height)
roof_info = roof_type_picker(height)

# Step 3
# =========================
# Streamlit wrapper (call from your code_jurisdiction_1 step)
# =========================
def code_jurisdiction_icc(city: str, state: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """
    Returns (ibc_year, iecc_year, state_url) with graceful failures.
    City is accepted for UI completeness but not used in ICC lookup (state-level).
    """
    try:
        res = lookup_icc_state_adoption(state)
        return res.ibc_year, res.iecc_year, res.state_url
    except Exception:
        return None, None, None


# Step 4
risk_category = risk_category()

# Step 5
V = wind_speed()

# Step 6
exposure, Kz, q = wind_pressure_calc(height, V)

