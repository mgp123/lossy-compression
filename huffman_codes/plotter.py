import matplotlib.pyplot as plt
import pandas as pd 
import plotly.express as px
import plotly.io as pio
import plotly.figure_factory as ff


df = pd.read_csv ('data_512.csv')

template = "seaborn"
fig = ff.create_distplot([df[c] for c in df.columns], df.columns, bin_size=2)
fig.add_vline(
    x=24, line_width=3, line_dash="dash", line_color="red",
    )

fig.add_annotation(
    text="24 bits line", 
    xref="x",
    yref="y",
    x=24,
    y=0.1,
    ax=60,
    showarrow=True,
    font_size=20,
    arrowsize=1,
    arrowwidth=2,)
margin=dict(l=80, r=80, t=100, b=80)
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    
)

pio.write_html(
    fig, 
    file="entropy.html", 
    auto_open=True,
    config={
        'displayModeBar': False,
        'displaylogo': False,                                       
        'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines']
    }
    )
