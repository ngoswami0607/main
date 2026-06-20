import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Effective wind areas requested
areas = [10, 20, 50, 100, 200, 500, 1000]

# Approximate ASCE 7 C&C GCp values digitized from the figures
# Verify against your actual ASCE 7 figure/table before final design use.

wall_data = {
    "Area (sf)": areas,
    "Wall Zone 4 Negative": [-1.1, -1.1, -1.0, -0.95, -0.90, -0.80, -0.80],
    "Wall Zone 5 Negative": [-1.4, -1.4, -1.25, -1.10, -1.00, -0.80, -0.80],
    "Wall Zone 4 & 5 Positive": [1.0, 1.0, 0.95, 0.90, 0.80, 0.70, 0.70],
}

roof_data = {
    "Area (sf)": areas,
    "Roof Zone 1 Negative": [-1.6, -1.6, -1.45, -1.35, -1.25, -1.0, -1.0],
    "Roof Zone 2 Negative": [-2.3, -2.3, -2.1, -1.9, -1.7, -1.4, -1.4],
    "Roof Zone 3 Negative": [-3.2, -3.2, -2.7, -2.4, -2.1, -1.4, -1.4],
    "Roof Zone 1 Positive": [0.9, 0.9, 0.85, 0.75, 0.60, 0.40, 0.40],
    "Roof Zones 1,2,3 Positive": [0.2, 0.2, 0.2, 0.25, 0.25, 0.25, 0.25],
}

wall_df = pd.DataFrame(wall_data)
roof_df = pd.DataFrame(roof_data)

st.title("External Pressure Coefficient, GCp")

selection = st.radio("Select Component", ["Walls", "Roof"])

df = wall_df if selection == "Walls" else roof_df

st.subheader(f"{selection} GCp Table")
st.dataframe(df, use_container_width=True)

fig = go.Figure()

# Plot GCp curves
for col in df.columns[1:]:
    fig.add_trace(
        go.Scatter(
            x=df["Area (sf)"],
            y=df[col],
            mode="lines+markers",
            name=col,
        )
    )

# Add vertical guide lines
for area in areas:
    fig.add_vline(
        x=area,
        line_width=1,
        line_dash="dot",
        opacity=0.5,
    )

# Add horizontal guide lines
y_values = sorted(set(df.drop(columns=["Area (sf)"]).values.flatten()))
for y in y_values:
    fig.add_hline(
        y=y,
        line_width=1,
        line_dash="dot",
        opacity=0.35,
    )

fig.update_layout(
    title=f"External Pressure Coefficient, GCp - {selection}",
    xaxis_title="Effective Wind Area, A (sq. ft.)",
    yaxis_title="GCp",
    xaxis=dict(
        type="log",
        tickvals=areas,
        ticktext=[str(a) for a in areas],
    ),
    yaxis=dict(
        autorange="reversed" if selection == "Walls" else False,
        zeroline=True,
    ),
    hovermode="x unified",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)
