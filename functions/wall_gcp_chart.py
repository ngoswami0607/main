import math
import numpy as np
import plotly.graph_objects as go


def wall_gcp(area):


    if area <=10:

        return (
            1.0,
            -1.1,
            -1.4
        )


    elif area <=500:

        logA = math.log10(area)

        positive = (
            1.1766 -
            0.1766*logA
        )

        zone4 = (
            -1.2766 +
            0.1766*logA
        )

        zone5 = (
            -1.7532 +
            0.3532*logA
        )

        return positive, zone4, zone5


    else:

        return (
            0.7,
            -0.8,
            -0.8
        )



def create_wall_chart(selected_area):


    x = np.logspace(
        0,
        3,
        300
    )


    pos=[]
    z4=[]
    z5=[]


    for a in x:

        p,z4n,z5n = wall_gcp(a)

        pos.append(p)
        z4.append(z4n)
        z5.append(z5n)



    selected = wall_gcp(selected_area)


    fig=go.Figure()


    fig.add_trace(
        go.Scatter(
            x=x,
            y=pos,
            name="Zones 4&5 Positive"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=x,
            y=z4,
            name="Zone 4 Negative"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=x,
            y=z5,
            name="Zone 5 Negative"
        )
    )


    fig.add_vline(
        x=selected_area,
        line_dash="dash",
        line_color="red"
    )


    fig.update_xaxes(
        type="log",
        range=[0,3],
        tickmode="array",
        tickvals=[1, 10,20,50,100,200,500,1000],
        ticktext=["1","10", "20", "50", "100", "200", "500", "1000"    ]
    )

    fig.update_yaxes(
        range=[1.2,-1.8]
    )


    fig.update_layout(
        title=
        "Components and Cladding [h ≤ 60 ft] (Figure 30.3-1)",
        height=600
    )


    return fig
