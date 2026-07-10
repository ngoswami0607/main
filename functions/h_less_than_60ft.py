import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw


def show_h_less_than_60ft(
    height,
    q,
    gcpi_positive,
    gcpi_negative,
):
    """
    Display GCp values and calculate ASCE 7-16 C&C pressures
    for buildings with mean roof height less than 60 ft.

    Parameters
    ----------
    height : float - Mean roof height, ft.
    q : float - Velocity pressure used for components and cladding, psf.
    gcpi_positive : float - Positive internal pressure coefficient.
    gcpi_negative : float - Negative internal pressure coefficient.
    """

    if height >= 60:
        return

    st.markdown(
        "### ASCE 7-16 Components & Cladding GCp for h < 60 ft"
    )

    areas = [10, 20, 50, 100, 200, 500, 1000]

    wall_df = pd.DataFrame({
        "Area (sf)": areas,
        "Wall Zone 4 Negative": [-1.1, -1.1, -1.0, -0.95, -0.90, -0.80, -0.80],
        "Wall Zone 5 Negative": [-1.4, -1.4, -1.25, -1.10, -1.00, -0.80, -0.80],
        "Wall Zone 4 & 5 Positive": [1.0, 1.0, 0.95, 0.90, 0.80, 0.70, 0.70],
    })

    roof_df = pd.DataFrame({
        "Area (sf)": areas,
        "Roof Zone 1 Negative": [-1.6, -1.6, -1.45, -1.35, -1.25, -1.0, -1.0],
        "Roof Zone 2 Negative": [-2.3, -2.3, -2.1, -1.9, -1.7, -1.4, -1.4],
        "Roof Zone 3 Negative": [-3.2, -3.2, -2.7, -2.4, -2.1, -1.4, -1.4],
        "Roof Zone 1 Positive": [0.9, 0.9, 0.85, 0.75, 0.60, 0.40, 0.40],
        "Roof Zones 1,2,3 Positive": [0.2, 0.2, 0.2, 0.25, 0.25, 0.25, 0.25],
    })

    def interpolate_gcp(area, dataframe, gcp_column):
        """
        Interpolate GCp using the logarithm of effective wind area.
        """

        area = float(area)

        area = max(
            float(dataframe["Area (sf)"].min()),
            min(area, float(dataframe["Area (sf)"].max())),
        )

        return float(
            np.interp(
                math.log10(area),
                np.log10(dataframe["Area (sf)"].astype(float)),
                dataframe[gcp_column].astype(float),
            )
        )

    def calculate_pressure(gcp, pressure_case):
        """
        Calculate net ASD C&C pressure:

            p = 0.6*q*(GCp - GCpi)

        ASD Positive external pressure is combined with negative GCpi.
        ASD Negative external pressure is combined with positive GCpi.
        """

        if pressure_case.lower() == "positive":
            return 0.6*q * (gcp - gcpi_negative)

        if pressure_case.lower() == "negative":
            return 0.6*q * (gcp - gcpi_positive)

        raise ValueError(
            "pressure_case must be either 'positive' or 'negative'."
        )

    # ---------------------------------------------------------
    # Create complete pressure table
    # ---------------------------------------------------------

    pressure_rows = []

    for area in areas:
        roof_z1_positive_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zone 1 Positive",
        )

        roof_z1_negative_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zone 1 Negative",
        )

        roof_z2_positive_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zones 1,2,3 Positive",
        )

        roof_z2_negative_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zone 2 Negative",
        )

        roof_z3_positive_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zones 1,2,3 Positive",
        )

        roof_z3_negative_gcp = interpolate_gcp(
            area,
            roof_df,
            "Roof Zone 3 Negative",
        )

        wall_z4_positive_gcp = interpolate_gcp(
            area,
            wall_df,
            "Wall Zone 4 & 5 Positive",
        )

        wall_z4_negative_gcp = interpolate_gcp(
            area,
            wall_df,
            "Wall Zone 4 Negative",
        )

        wall_z5_positive_gcp = interpolate_gcp(
            area,
            wall_df,
            "Wall Zone 4 & 5 Positive",
        )

        wall_z5_negative_gcp = interpolate_gcp(
            area,
            wall_df,
            "Wall Zone 5 Negative",
        )

        pressure_rows.append(
            {
                "Effective Wind Area (sf)": area,

                "Roof Zone 1 Positive (psf)":
                    calculate_pressure(
                        roof_z1_positive_gcp,
                        "positive",
                    ),

                "Roof Zone 1 Negative (psf)":
                    calculate_pressure(
                        roof_z1_negative_gcp,
                        "negative",
                    ),

                "Roof Zone 2 Positive (psf)":
                    calculate_pressure(
                        roof_z2_positive_gcp,
                        "positive",
                    ),

                "Roof Zone 2 Negative (psf)":
                    calculate_pressure(
                        roof_z2_negative_gcp,
                        "negative",
                    ),

                "Roof Zone 3 Positive (psf)":
                    calculate_pressure(
                        roof_z3_positive_gcp,
                        "positive",
                    ),

                "Roof Zone 3 Negative (psf)":
                    calculate_pressure(
                        roof_z3_negative_gcp,
                        "negative",
                    ),

                "Wall Zone 4 Positive (psf)":
                    calculate_pressure(
                        wall_z4_positive_gcp,
                        "positive",
                    ),

                "Wall Zone 4 Negative (psf)":
                    calculate_pressure(
                        wall_z4_negative_gcp,
                        "negative",
                    ),

                "Wall Zone 5 Positive (psf)":
                    calculate_pressure(
                        wall_z5_positive_gcp,
                        "positive",
                    ),

                "Wall Zone 5 Negative (psf)":
                    calculate_pressure(
                        wall_z5_negative_gcp,
                        "negative",
                    ),
            }
        )

    pressure_df = pd.DataFrame(pressure_rows)

    def wall_gcp_values(effective_area):
    """
    Calculate wall GCp values from ASCE 7-16 Table C30.3-1.

    Parameters
    ----------
    effective_area : float
        Effective wind area, ft².

    Returns
    -------
    tuple
        Positive Zones 4 & 5 GCp,
        Negative Zone 4 GCp,
        Negative Zone 5 GCp.
    """

    area = float(effective_area)

    if area <= 10:
        positive_gcp = 1.00
        zone_4_negative_gcp = -1.10
        zone_5_negative_gcp = -1.40

    elif area <= 500:
        log_area = math.log10(area)

        positive_gcp = 1.1766 - 0.1766 * log_area

        zone_4_negative_gcp = (
            -1.2766 + 0.1766 * log_area
        )

        zone_5_negative_gcp = (
            -1.7532 + 0.3532 * log_area
        )

    else:
        positive_gcp = 0.70
        zone_4_negative_gcp = -0.80
        zone_5_negative_gcp = -0.80

    return (
        positive_gcp,
        zone_4_negative_gcp,
        zone_5_negative_gcp,
    )


def create_wall_gcp_dataframe():
    """
    Create GCp values at the standard effective wind areas.
    """

    standard_areas = [10, 20, 50, 100, 200, 500, 1000]

    rows = []

    for area in standard_areas:
        positive, zone_4_negative, zone_5_negative = (
            wall_gcp_values(area)
        )

        rows.append(
            {
                "Area (sf)": area,
                "Wall Zones 4 & 5 Positive": positive,
                "Wall Zone 4 Negative": zone_4_negative,
                "Wall Zone 5 Negative": zone_5_negative,
            }
        )

    return pd.DataFrame(rows)


def create_wall_gcp_chart(selected_area):
    """
    Create an interactive wall GCp chart with a logarithmic x-axis
    and reversed y-axis.
    """

    chart_areas = np.logspace(
        math.log10(10),
        math.log10(1000),
        250,
    )

    positive_values = []
    zone_4_negative_values = []
    zone_5_negative_values = []

    for area in chart_areas:
        positive, zone_4_negative, zone_5_negative = (
            wall_gcp_values(area)
        )

        positive_values.append(positive)
        zone_4_negative_values.append(zone_4_negative)
        zone_5_negative_values.append(zone_5_negative)

    (
        selected_positive,
        selected_zone_4_negative,
        selected_zone_5_negative,
    ) = wall_gcp_values(selected_area)

    fig = go.Figure()

    # Positive Zones 4 and 5
    fig.add_trace(
        go.Scatter(
            x=chart_areas,
            y=positive_values,
            mode="lines",
            name="Zones 4 & 5 Positive",
            line=dict(width=3),
            hovertemplate=(
                "Area: %{x:.1f} ft²"
                "<br>GCp: %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Negative Zone 4
    fig.add_trace(
        go.Scatter(
            x=chart_areas,
            y=zone_4_negative_values,
            mode="lines",
            name="Zone 4 Negative",
            line=dict(width=3),
            hovertemplate=(
                "Area: %{x:.1f} ft²"
                "<br>GCp: %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Negative Zone 5
    fig.add_trace(
        go.Scatter(
            x=chart_areas,
            y=zone_5_negative_values,
            mode="lines",
            name="Zone 5 Negative",
            line=dict(width=3),
            hovertemplate=(
                "Area: %{x:.1f} ft²"
                "<br>GCp: %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Selected-area markers
    fig.add_trace(
        go.Scatter(
            x=[
                selected_area,
                selected_area,
                selected_area,
            ],
            y=[
                selected_positive,
                selected_zone_4_negative,
                selected_zone_5_negative,
            ],
            mode="markers+text",
            name="Selected Area",
            marker=dict(
                size=11,
                color="black",
            ),
            text=[
                f"{selected_positive:.3f}",
                f"{selected_zone_4_negative:.3f}",
                f"{selected_zone_5_negative:.3f}",
            ],
            textposition=[
                "bottom right",
                "top right",
                "top right",
            ],
            hovertemplate=(
                "Area: %{x:.1f} ft²"
                "<br>GCp: %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    # Vertical selected-area line
    fig.add_vline(
        x=selected_area,
        line_width=2,
        line_dash="dash",
        line_color="red",
        annotation_text=f"A = {selected_area:.0f} ft²",
        annotation_position="top",
    )

    # Zero-pressure reference line
    fig.add_hline(
        y=0,
        line_width=1,
        line_color="gray",
    )

    fig.update_layout(
        title=(
            "Components and Cladding "
            "[h ≤ 60 ft (h ≤ 18.3 m)] "
            "(Figure 30.3-1)"
        ),
        xaxis_title="Effective Wind Area, A (ft²)",
        yaxis_title="External Pressure Coefficient, GCp",
        hovermode="x unified",
        height=650,
        margin=dict(
            left=70,
            right=40,
            top=90,
            bottom=70,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(
        type="log",
        tickmode="array",
        tickvals=[
            10,
            20,
            50,
            100,
            200,
            500,
            1000,
        ],
        ticktext=[
            "10",
            "20",
            "50",
            "100",
            "200",
            "500",
            "1000",
        ],
        showgrid=True,
        minor=dict(showgrid=True),
    )

    # Reverse the y-axis so negative values appear at the top
    fig.update_yaxes(
        autorange="reversed",
        range=[1.2, -1.8],
        tick0=-1.8,
        dtick=0.2,
        showgrid=True,
        zeroline=True,
    )

    return fig


    # ---------------------------------------------------------
    # User-selected GCp calculations
    # ---------------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Wall GCp",
            "Roof GCp",
            "Pressure Table",
        ]
    )

    with tab1:
    st.markdown(
        "#### Wall External Pressure Coefficient, GCp"
    )

    wall_area = st.slider(
        "Effective Wind Area for Wall, A (ft²)",
        min_value=10,
        max_value=1000,
        value=10,
        step=1,
        key="wall_area_slider",
    )

    (
        wall_positive_gcp,
        wall_zone_4_negative_gcp,
        wall_zone_5_negative_gcp,
    ) = wall_gcp_values(wall_area)

    # Net pressures
    wall_positive_pressure = q * (
        wall_positive_gcp - gcpi_negative
    )

    wall_zone_4_negative_pressure = q * (
        wall_zone_4_negative_gcp - gcpi_positive
    )

    wall_zone_5_negative_pressure = q * (
        wall_zone_5_negative_gcp - gcpi_positive
    )

    st.markdown("##### GCp at Selected Effective Area")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Zones 4 & 5 Positive GCp",
            value=f"{wall_positive_gcp:+.3f}",
            delta=(
                f"Pressure: "
                f"{wall_positive_pressure:+.2f} psf"
            ),
            delta_color="off",
        )

    with col2:
        st.metric(
            label="Zone 4 Negative GCp",
            value=f"{wall_zone_4_negative_gcp:+.3f}",
            delta=(
                f"Pressure: "
                f"{wall_zone_4_negative_pressure:+.2f} psf"
            ),
            delta_color="off",
        )

    with col3:
        st.metric(
            label="Zone 5 Negative GCp",
            value=f"{wall_zone_5_negative_gcp:+.3f}",
            delta=(
                f"Pressure: "
                f"{wall_zone_5_negative_pressure:+.2f} psf"
            ),
            delta_color="off",
        )

    st.caption(
        f"Selected effective area = {wall_area:.0f} ft² | "
        f"q = {q:.2f} psf | "
        f"GCpi positive = {gcpi_positive:+.2f} | "
        f"GCpi negative = {gcpi_negative:+.2f}"
    )

    wall_chart = create_wall_gcp_chart(wall_area)

    st.plotly_chart(
        wall_chart,
        use_container_width=True,
        key="wall_gcp_interactive_chart",
    )

    with st.expander(
        "Show Wall GCp Values",
        expanded=False,
    ):
        st.dataframe(
            wall_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Area (sf)": st.column_config.NumberColumn(
                    "Effective Area (ft²)",
                    format="%.0f",
                ),
                "Wall Zones 4 & 5 Positive":
                    st.column_config.NumberColumn(
                        "Zones 4 & 5 Positive",
                        format="%.3f",
                    ),
                "Wall Zone 4 Negative":
                    st.column_config.NumberColumn(
                        "Zone 4 Negative",
                        format="%.3f",
                    ),
                "Wall Zone 5 Negative":
                    st.column_config.NumberColumn(
                        "Zone 5 Negative",
                        format="%.3f",
                    ),
            },
        )

    with tab2:
        st.markdown(
            "#### Roof External Pressure Coefficient, GCp"
        )

        roof_area = st.number_input(
            "Effective Wind Area for Roof, A (sq. ft.)",
            min_value=10.0,
            max_value=1000.0,
            value=10.0,
            step=10.0,
            key="roof_area_input",
        )

        roof_case = st.selectbox(
            "Select Roof Zone / Pressure Case",
            [
                "Roof Zone 1 Negative",
                "Roof Zone 2 Negative",
                "Roof Zone 3 Negative",
                "Roof Zone 1 Positive",
                "Roof Zones 1,2,3 Positive",
            ],
            key="roof_case_select",
        )

        roof_gcp = interpolate_gcp(
            roof_area,
            roof_df,
            roof_case,
        )

        if "Positive" in roof_case:
            roof_pressure = calculate_pressure(
                roof_gcp,
                "positive",
            )
            governing_gcpi = gcpi_negative
        else:
            roof_pressure = calculate_pressure(
                roof_gcp,
                "negative",
            )
            governing_gcpi = gcpi_positive

        st.success(
            f"{roof_case}: "
            f"GCp = {roof_gcp:.2f}, "
            f"GCpi = {governing_gcpi:+.2f}, "
            f"Pressure = {roof_pressure:.2f} psf "
            f"at A = {roof_area:.0f} sq. ft."
        )

        roof_image = draw_gcp_on_image(
            image_path=(
                "Gcp Figures_image/"
                "Less than 60_roof.png"
            ),
            area=roof_area,
            gcp=roof_gcp,
            figure_type="roof",
        )

        if roof_image is not None:
            st.image(
                roof_image,
                caption=(
                    "Roof GCp figure with selected effective "
                    "wind area and GCp"
                ),
                width=700,
            )

        st.dataframe(
            roof_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        st.markdown("#### Components & Cladding Design Pressures")

        st.caption(
            f"q = {q:.2f} psf | "
            f"GCpi positive = {gcpi_positive:+.2f} | "
            f"GCpi negative = {gcpi_negative:+.2f}"
        )

    # ---------------------------------------------------------
    # Separate pressure table into roof and wall tables
    # ---------------------------------------------------------

        roof_pressure_df = pressure_df[
            [
                "Effective Wind Area (sf)",
                "Roof Zone 1 Positive (psf)",
                "Roof Zone 1 Negative (psf)",
                "Roof Zone 2 Positive (psf)",
                "Roof Zone 2 Negative (psf)",
                "Roof Zone 3 Positive (psf)",
                "Roof Zone 3 Negative (psf)",
            ]
        ].copy()

        wall_pressure_df = pressure_df[
            [
                "Effective Wind Area (sf)",
                "Wall Zone 4 Positive (psf)",
                "Wall Zone 4 Negative (psf)",
                "Wall Zone 5 Positive (psf)",
                "Wall Zone 5 Negative (psf)",
            ]
        ].copy()

        st.markdown("##### Roof Zone Design Pressures")

        st.dataframe(
            roof_pressure_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Effective Wind Area (sf)": st.column_config.NumberColumn(
                    "Effective Area (sf)",
                    format="%.0f",
                ),
                "Roof Zone 1 Positive (psf)": st.column_config.NumberColumn(
                    "Zone 1 + (psf)",
                    format="%.2f",
                ),
                "Roof Zone 1 Negative (psf)": st.column_config.NumberColumn(
                    "Zone 1 − (psf)",
                    format="%.2f",
                ),
                "Roof Zone 2 Positive (psf)": st.column_config.NumberColumn(
                    "Zone 2 + (psf)",
                    format="%.2f",
                ),
                "Roof Zone 2 Negative (psf)": st.column_config.NumberColumn(
                    "Zone 2 − (psf)",
                    format="%.2f",
                ),
                "Roof Zone 3 Positive (psf)": st.column_config.NumberColumn(
                    "Zone 3 + (psf)",
                    format="%.2f",
                ),
                "Roof Zone 3 Negative (psf)": st.column_config.NumberColumn(
                    "Zone 3 − (psf)",
                    format="%.2f",
                ),
            },
        )

        st.markdown("##### Wall Zone Design Pressures")

        st.dataframe(
            wall_pressure_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Effective Wind Area (sf)": st.column_config.NumberColumn(
                    "Effective Area (sf)",
                    format="%.0f",
                ),
                "Wall Zone 4 Positive (psf)": st.column_config.NumberColumn(
                    "Zone 4 + (psf)",
                    format="%.2f",
                ),
                "Wall Zone 4 Negative (psf)": st.column_config.NumberColumn(
                    "Zone 4 − (psf)",
                    format="%.2f",
                ),
                "Wall Zone 5 Positive (psf)": st.column_config.NumberColumn(
                    "Zone 5 + (psf)",
                    format="%.2f",
                ),
                "Wall Zone 5 Negative (psf)": st.column_config.NumberColumn(
                    "Zone 5 − (psf)",
                    format="%.2f",
                ),
            },
        )

    return pressure_df
