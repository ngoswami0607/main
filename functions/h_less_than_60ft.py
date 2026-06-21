import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image, ImageDraw
import numpy as np
import math


def show_h_less_than_60ft(mean_roof_height):
    if mean_roof_height >= 60:
        return

    st.markdown("### ASCE 7-16 GCp Figures for h < 60 ft")

    tab1, tab2 = st.tabs(["Wall GCp", "Roof GCp"])

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

def interpolate_gcp(area, x_values, y_values):
    return np.interp(area, x_values, y_values)


def draw_wall_gcp_on_image(image_path, area, gcp):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Adjust these values if line is slightly off
    plot_left = 175
    plot_right = 545
    plot_top = 55
    plot_bottom = 275

    x_min = math.log10(1)
    x_max = math.log10(1000)

    y_min = -1.8
    y_max = 1.2

    # Convert area to x-coordinate using log scale
    x = plot_left + (math.log10(area) - x_min) / (x_max - x_min) * (plot_right - plot_left)

    # Convert GCp to y-coordinate
    y = plot_top + (gcp - y_min) / (y_max - y_min) * (plot_bottom - plot_top)

    # Vertical line for effective wind area
    draw.line([(x, plot_top), (x, plot_bottom)], fill="red", width=3)

    # Horizontal line for GCp
    draw.line([(plot_left, y), (plot_right, y)], fill="blue", width=3)

    # Point at intersection
    r = 6
    draw.ellipse((x-r, y-r, x+r, y+r), fill="black")

    return img

with tab1:
    st.markdown("#### Wall GCp")

    area_input = st.number_input(
        "Enter Effective Wind Area for Wall, A (sq. ft.)",
        min_value=1.0,
        max_value=1000.0,
        value=10.0,
        step=1.0
    )

    zone_choice = st.selectbox(
        "Select Wall Zone / Pressure Case",
        [
            "Wall Zone 4 Negative",
            "Wall Zone 5 Negative",
            "Wall Zone 4 & 5 Positive"
        ]
    )

    areas = [10, 20, 50, 100, 200, 500, 1000]

    wall_df = pd.DataFrame({
        "Area (sf)": areas,
        "Wall Zone 4 Negative": [-1.1, -1.1, -1.0, -0.95, -0.90, -0.80, -0.80],
        "Wall Zone 5 Negative": [-1.4, -1.4, -1.25, -1.10, -1.00, -0.80, -0.80],
        "Wall Zone 4 & 5 Positive": [1.0, 1.0, 0.95, 0.90, 0.80, 0.70, 0.70],
    })

    gcp_value = interpolate_gcp(
        area_input,
        wall_df["Area (sf)"],
        wall_df[zone_choice]
    )

    st.success(f"GCp for {zone_choice} at A = {area_input:.0f} sq. ft. is {gcp_value:.2f}")

    annotated_wall = draw_wall_gcp_on_image(
        "Gcp Figures_image/Less than 60_wall.png",
        area_input,
        gcp_value
    )

    st.image(
        annotated_wall,
        caption="Wall GCp figure with user-selected effective wind area and GCp line",
        use_container_width=True
    )

    st.dataframe(wall_df, use_container_width=True)
