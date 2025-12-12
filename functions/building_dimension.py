import plotly.graph_objects as go


def create_building_visualisation(NS_dimension, EW_dimension, z,
                                  include_inset=False, inset_offset=0, inset_height=0):
    # Colors
    TT_LightBlue = "rgb(136,219,223)"
    TT_LightGrey = "rgb(223,224,225)"

    L = float(NS_dimension)
    W = float(EW_dimension)
    H = float(z)

    fig = go.Figure()

    # --- Ground (simple surface) ---
    ground_extension = max(L, W) * 0.3
    xg0, xg1 = -ground_extension, L + ground_extension
    yg0, yg1 = -ground_extension, W + ground_extension

    fig.add_trace(go.Surface(
        x=[[xg0, xg1], [xg0, xg1]],
        y=[[yg0, yg0], [yg1, yg1]],
        z=[[0, 0], [0, 0]],
        showscale=False,
        opacity=0.6,
        hoverinfo="none",
        colorscale=[[0, TT_LightGrey], [1, TT_LightGrey]],
    ))

    # --- Building as ONE closed mesh (8 vertices, 12 triangles) ---
    # Vertex indices:
    # 0:(0,0,0) 1:(L,0,0) 2:(L,W,0) 3:(0,W,0)
    # 4:(0,0,H) 5:(L,0,H) 6:(L,W,H) 7:(0,W,H)
    x = [0, L, L, 0, 0, L, L, 0]
    y = [0, 0, W, W, 0, 0, W, W]
    zc = [0, 0, 0, 0, H, H, H, H]

    # 12 triangles (2 per face)
    i = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
    j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
    k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]

    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=zc,
        i=i, j=j, k=k,
        color=TT_LightBlue,
        opacity=0.95,
        flatshading=True,        # important: makes faces look planar
        hoverinfo="none",
        lighting=dict(ambient=0.7, diffuse=0.6, specular=0.1, roughness=0.9),
    ))

    # Optional: draw edges so it reads as a “box”
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    xe, ye, ze = [], [], []
    for a, b in edges:
        xe += [x[a], x[b], None]
        ye += [y[a], y[b], None]
        ze += [zc[a], zc[b], None]

    fig.add_trace(go.Scatter3d(
        x=xe, y=ye, z=ze,
        mode="lines",
        line=dict(width=4),
        hoverinfo="none",
        showlegend=False
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showgrid=False, showticklabels=False, showbackground=False, zeroline=False),
            yaxis=dict(visible=False, showgrid=False, showticklabels=False, showbackground=False, zeroline=False),
            zaxis=dict(visible=False, showgrid=False, showticklabels=False, showbackground=False, zeroline=False),
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=False,
        scene_camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
        height=420,
    )

    return fig
