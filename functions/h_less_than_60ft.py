import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
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

    def draw_gcp_on_image(
        image_path,
        area,
        gcp,
        figure_type="wall",
    ):
        """
        Draw area and GCp guide lines on the source ASCE figure.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            st.error(f"Image file not found: {image_path}")
            return None

        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        img_width, img_height = img.size

        st.caption(
            f"{figure_type.title()} figure image size: "
            f"{img_width} × {img_height} pixels"
        )

        with st.expander(
            f"Calibrate {figure_type.title()} Figure Boundary",
            expanded=False,
        ):
            col1, col2 = st.columns(2)

            with col1:
                plot_left = st.slider(
                    f"{figure_type}_plot_left",
                    min_value=0,
                    max_value=img_width,
                    value=int(img_width * 0.38),
                )

                plot_right = st.slider(
                    f"{figure_type}_plot_right",
                    min_value=0,
                    max_value=img_width,
                    value=int(img_width * 0.86),
                )

            with col2:
                plot_top = st.slider(
                    f"{figure_type}_plot_top",
                    min_value=0,
                    max_value=img_height,
                    value=int(img_height * 0.18),
                )

                plot_bottom = st.slider(
                    f"{figure_type}_plot_bottom",
                    min_value=0,
                    max_value=img_height,
                    value=int(img_height * 0.78),
                )

        if plot_right <= plot_left:
            st.error("Plot right must be greater than plot left.")
            return img

        if plot_bottom <= plot_top:
            st.error("Plot bottom must be greater than plot top.")
            return img

        if figure_type == "wall":
            y_top_gcp = -1.80
            y_bottom_gcp = 1.20
        else:
            y_top_gcp = -4.00
            y_bottom_gcp = 1.00

        x_min_area = 1.0
        x_max_area = 1000.0

        x = plot_left + (
            (
                math.log10(area)
                - math.log10(x_min_area)
            )
            / (
                math.log10(x_max_area)
                - math.log10(x_min_area)
            )
        ) * (plot_right - plot_left)

        y = plot_top + (
            (gcp - y_top_gcp)
            / (y_bottom_gcp - y_top_gcp)
        ) * (plot_bottom - plot_top)

        draw.line(
            [(x, plot_top), (x, plot_bottom)],
            fill="red",
            width=4,
        )

        draw.line(
            [(plot_left, y), (plot_right, y)],
            fill="blue",
            width=4,
        )

        radius = 7

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            fill="black",
        )

        return img

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

        wall_area = st.number_input(
            "Effective Wind Area for Wall, A (sq. ft.)",
            min_value=10.0,
            max_value=1000.0,
            value=10.0,
            step=10.0,
            key="wall_area_input",
        )

        wall_case = st.selectbox(
            "Select Wall Zone / Pressure Case",
            [
                "Wall Zone 4 Negative",
                "Wall Zone 5 Negative",
                "Wall Zone 4 & 5 Positive",
            ],
            key="wall_case_select",
        )

        wall_gcp = interpolate_gcp(
            wall_area,
            wall_df,
            wall_case,
        )

        if "Positive" in wall_case:
            wall_pressure = calculate_pressure(
                wall_gcp,
                "positive",
            )
            governing_gcpi = gcpi_negative
        else:
            wall_pressure = calculate_pressure(
                wall_gcp,
                "negative",
            )
            governing_gcpi = gcpi_positive

        st.success(
            f"{wall_case}: "
            f"GCp = {wall_gcp:.2f}, "
            f"GCpi = {governing_gcpi:+.2f}, "
            f"Pressure = {wall_pressure:.2f} psf "
            f"at A = {wall_area:.0f} sq. ft."
        )

        wall_image = draw_gcp_on_image(
            image_path=(
                "Gcp Figures_image/"
                "Less than 60_wall.png"
            ),
            area=wall_area,
            gcp=wall_gcp,
            figure_type="wall",
        )

        if wall_image is not None:
            st.image(
                wall_image,
                caption=(
                    "Wall GCp figure with selected effective "
                    "wind area and GCp"
                ),
                width=700,
            )

        st.dataframe(
            wall_df,
            use_container_width=True,
            hide_index=True,
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

        st.dataframe(
            styled_pressure_df,
            width="stretch",
            height=320,
            hide_index=True,
        )
    return pressure_df
