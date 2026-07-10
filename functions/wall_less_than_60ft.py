import streamlit as st

from functions.pressure_table import create_wall_pressure_table

from functions.GCP_h_Less_than_60 import (
    get_wall_gcp_data,
    get_roof_gcp_data
)

from functions.wall_gcp_chart import (
    create_wall_chart,
    wall_gcp
)


def show_wall_less_than_60ft(
    height,
    q,
    gcpi_positive,
    gcpi_negative
):

    if height >= 60:
        return


    st.header(
        "ASCE 7-16 Components & Cladding"
    )


    pressure_df = create_wall_pressure_table(
        q,
        gcpi_positive,
        gcpi_negative
    )


    tab1, tab2 = st.tabs(
        [
            "Wall GCp",
            "Pressure Table"
        ]
    )


    # -------------------------
    # WALL GCp TAB
    # -------------------------

    with tab1:

        st.markdown(
            "### Components and Cladding "
            "[h ≤ 60 ft (h ≤ 18.3 m)] "
            "(Figure 30.3-1)"
        )


        area = st.slider(
            "Effective Wind Area (ft²)",
            min_value=1,
            max_value=1000,
            value=10
        )


        positive, z4, z5 = wall_gcp(area)
        pressure1 = 0.6*q*(positive-gcpi_negative)
        pressure2 = 0.6*q*(z4-gcpi_negative)
        pressure3 = 0.6*q*(z5 - gcpi_positive)
        
        # GCp output boxes
        col1, col2, col3 = st.columns(3)
        with col1:st.metric("GCp Zone 4 & 5 Positive", f"{positive:+.3f}")
        with col2:st.metric("GCp Zone 4 Negative", f"{z4:+.3f}")
        with col3:st.metric("GCp Zone 5 Negative", f"{z5:+.3f}")
        
        # pressure output boxes
        col4, col5, col6 = st.columns(3)
        with col4:st.metric("Pressure Zone 4 & 5 Positive", f"{pressure1:+.2f} psf")
        with col5:st.metric("Pressure Zone 4 Negative", f"{pressure2:+.2f} psf")
        with col6:st.metric("Pressure Zone 5 Negative", f"{pressure3:+.2f} psf")

        fig = create_wall_chart(area)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.markdown(
            "#### GCp Values"
        )


        wall_df = get_wall_gcp_data()


        st.dataframe(
            wall_df,
            width="stretch",
            hide_index=True
        )


    # -------------------------
    # PRESSURE TAB
    # -------------------------

    with tab2:

        st.markdown("### ASD Components and Cladding Design Load [h ≤ 60 ft (h ≤ 18.3 m)] (Figure 30.3-1)")

        st.caption(
            f"q = {q:.2f} psf | "
            f"GCpi + = {gcpi_positive:+.2f} | "
            f"GCpi - = {gcpi_negative:+.2f}"
        )


        st.dataframe(
            pressure_df,
            width="stretch",
            hide_index=True
        )
