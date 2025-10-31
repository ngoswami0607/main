import streamlit as st

def wind_speed():
    st.header("4️⃣ Wind Speed")
    st.markdown("Get your wind speed (V) from [ASCE Hazard Tool](https://ascehazardtool.org/)")
    V = st.number_input("Enter Basic Wind Speed (mph)", min_value=0.0, value=115.0)
    st.success(f"Using V = {V:.1f} mph")
    st.markdown("---")
    return V
