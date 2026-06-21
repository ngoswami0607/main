import streamlit as st
import pandas as pd
import plotly.graph_objects as go


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

    def plot_gcp(df, title):
        fig = go.Figure()

        for col in df.columns[1:]:
            fig.add_trace(
                go.Scatter(
                    x=df["Area (sf)"],
                    y=df[col],
                    mode="lines+markers",
                    name=col,
                )
            )

        for area in areas:
            fig.add_vline(x=area, line_width=1, line_dash="dot", opacity=0.45)

        y_values = sorted(set(df.drop(columns=["Area (sf)"]).values.flatten()))
        for y in y_values:
            fig.add_hline(y=y, line_width=1, line_dash="dot", opacity=0.30)

        fig.update_layout(
            title=title,
            xaxis_title="Effective Wind Area, A (sq. ft.)",
            yaxis_title="External Pressure Coefficient, GCp",
            xaxis=dict(
                type="log",
                tickvals=areas,
                ticktext=[str(a) for a in areas],
            ),
            hovermode="x unified",
            height=500,
        )

        return fig

    with tab1:
        st.image("Gcp Figures_image/Less than 60_wall.png", caption="ASCE 7-16 Wall GCp Figure")
        st.dataframe(wall_df, use_container_width=True)
        st.plotly_chart(plot_gcp(wall_df, "Wall External Pressure Coefficient, GCp"), use_container_width=True)

    with tab2:
        st.image("Gcp Figures_image/Less than 60_roof.png", caption="ASCE 7-16 Roof GCp Figure")
        st.dataframe(roof_df, use_container_width=True)
        st.plotly_chart(plot_gcp(roof_df, "Roof External Pressure Coefficient, GCp"), use_container_width=True)
