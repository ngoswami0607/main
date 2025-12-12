import streamlit as st
from functions.create_building_visualisation import create_building_visualisation

def building_dimension():
    """
    Streamlit step:
    - asks for NS, EW, height
    - plots building
    - returns (least_width, longest_width, height)
    """
    st.header("1️⃣ Building Dimensions")

    c1, c2, c3 = st.columns(3)
    ns = c1.number_input("North–South (ft)", min_value=0.01, value=80.0, format="%.2f", key="bd_ns")
    ew = c2.number_input("East–West (ft)", min_value=0.01, value=60.0, format="%.2f", key="bd_ew")
    height = c3.number_input("Mean Roof Height (ft)", min_value=0.01, value=30.0, format="%.2f", key="bd_h")

    least_width = float(min(ns, ew))
    longest_width = float(max(ns, ew))

    fig = create_building_visualisation(ns, ew, height)
    st.plotly_chart(fig, use_container_width=True)

    return least_width, longest_width, float(height)
