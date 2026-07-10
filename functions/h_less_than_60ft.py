import streamlit as st

from functions.gcp_data import (
    get_wall_gcp_data,
    get_roof_gcp_data
)

from functions.wall_gcp_chart import (
    create_wall_chart,
    wall_gcp
)


def show_h_less_than_60ft(
    height,
    q,
    gcpi_positive,
    gcpi_negative
):

    if height >=60:
        return


    st.header(
        "ASCE 7-16 Components & Cladding"
    )


    wall_df = get_wall_gcp_data()


    tab1,tab2 = st.tabs(
        [
            "Wall GCp",
            "Pressure Table"
        ]
    )


    with tab1:


        area = st.slider(
            "Effective Wind Area",
            10,
            1000,
            10
        )


        positive,z4,z5 = wall_gcp(area)


        st.write(
            f"Positive GCp = {positive:.3f}"
        )

        st.write(
            f"Zone 4 GCp = {z4:.3f}"
        )

        st.write(
            f"Zone 5 GCp = {z5:.3f}"
        )


        fig=create_wall_chart(area)

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with tab2:

        st.dataframe(
            wall_df
        )
