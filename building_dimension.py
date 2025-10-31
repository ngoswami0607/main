import streamlit as st
import plotly.graph_objects as go

def building_dimension():
    """Step 1 - Building Dimensions and 3D visualization"""

    st.header("1️⃣ Building Dimensions")

    col1, col2, col3 = st.columns(3)
    least_width = col1.number_input("Least Width (ft)", min_value=0.0, value=30.0, format="%.2f")
    longest_width = col2.number_input("Longest Width (ft)", min_value=0.0, value=80.0, format="%.2f")
    height = col3.number_input("Mean Roof Height (ft)", min_value=0.0, value=30.0, format="%.2f")

    st.markdown(f"""
    **Summary:**  
    - Least Width (x): `{least_width} ft`  
    - Longest Width (y): `{longest_width} ft`  
    - Height (z): `{height} ft`
    """)

    # Build 3D visualization
    x = [0, least_width, least_width, 0, 0, least_width, least_width, 0]
    y = [0, 0, longest_width, longest_width, 0, 0, longest_width, longest_width]
    z = [0, 0, 0, 0, height, height, height, height]

    i = [0, 0, 0, 1, 1, 2, 3, 4, 4, 5, 6, 7]
    j = [1, 2, 3, 2, 5, 3, 7, 5, 6, 6, 7, 4]
    k = [5, 3, 4, 5, 6, 7, 4, 6, 7, 4, 4, 5]

    fig = go.Figure(data=[
        go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color='lightblue', opacity=1.0)
    ])

    # Add edges
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for e in edges:
        fig.add_trace(go.Scatter3d(
            x=[x[e[0]], x[e[1]]],
            y=[y[e[0]], y[e[1]]],
            z=[z[e[0]], z[e[1]]],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False
        ))

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    return least_width, longest_width, height
