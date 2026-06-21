import math
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw


def show_h_less_than_60ft(height):
    """
    Shows ASCE 7-16 GCp figures and values for buildings with mean roof height < 60 ft.
    """

    if height >= 60:
        return

    st.markdown("### ASCE 7-16 Components & Cladding GCp for h < 60 ft")

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

    def interpolate_gcp(area, df, gcp_column):
        return np.interp(area, df["Area (sf)"], df[gcp_column])

def draw_wall_gcp_on_image(image_path, area, gcp):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Plot limits for wall figure
    plot_left = 306
    plot_right = 674
    plot_top = 82
    plot_bottom = 388

    x_min_area = 1
    x_max_area = 1000

    y_top_gcp = -1.8
    y_bottom_gcp = 1.2

    x = plot_left + (
        (math.log10(area) - math.log10(x_min_area))
        / (math.log10(x_max_area) - math.log10(x_min_area))
    ) * (plot_right - plot_left)

    y = plot_top + (
        (gcp - y_top_gcp)
        / (y_bottom_gcp - y_top_gcp)
    ) * (plot_bottom - plot_top)

    draw.line([(x, plot_top), (x, plot_bottom)], fill="red", width=4)
    draw.line([(plot_left, y), (plot_right, y)], fill="blue", width=4)

    r = 7
    draw.ellipse((x-r, y-r, x+r, y+r), fill="black")

    return img
      
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        x = plot_left + (
            (math.log10(area) - math.log10(x_min_area))
            / (math.log10(x_max_area) - math.log10(x_min_area))
        ) * (plot_right - plot_left)

        y = plot_top + (
            (gcp - y_max_gcp) / (y_min_gcp - y_max_gcp)
        ) * (plot_bottom - plot_top)

        draw.line([(x, plot_top), (x, plot_bottom)], fill="red", width=3)
        draw.line([(plot_left, y), (plot_right, y)], fill="blue", width=3)

        r = 6
        draw.ellipse((x - r, y - r, x + r, y + r), fill="black")

        return img

    tab1, tab2 = st.tabs(["Wall GCp", "Roof GCp"])

    with tab1:
        st.markdown("#### Wall External Pressure Coefficient, GCp")

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

        wall_gcp = interpolate_gcp(wall_area, wall_df, wall_case)

        st.success(f"{wall_case}: GCp = {wall_gcp:.2f} at A = {wall_area:.0f} sq. ft.")

        wall_image = draw_wall_gcp_on_image("Gcp Figures_image/Less than 60_wall.png",wall_area,wall_gcp)

        st.image(
            wall_image,
            caption="Wall GCp figure with selected effective wind area and GCp",
            use_container_width=True,
        )

        st.dataframe(wall_df, use_container_width=True)

    with tab2:
        st.markdown("#### Roof External Pressure Coefficient, GCp")

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

        roof_gcp = interpolate_gcp(roof_area, roof_df, roof_case)

        st.success(
            f"{roof_case}: GCp = {roof_gcp:.2f} at A = {roof_area:.0f} sq. ft."
        )

        roof_image = draw_gcp_lines_on_image(
            image_path="Gcp Figures_image/Less than 60_roof.png",
            area=roof_area,
            gcp=roof_gcp,
            plot_left=155,
            plot_right=555,
            plot_top=45,
            plot_bottom=300,
            x_min_area=1,
            x_max_area=1000,
            y_min_gcp=1.0,
            y_max_gcp=-4.0,
        )

        st.image(
            roof_image,
            caption="Roof GCp figure with selected effective wind area and GCp",
            use_container_width=True,
        )

        st.dataframe(roof_df, use_container_width=True)
