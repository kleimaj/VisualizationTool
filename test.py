### Importing packages

import numpy as np
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import os

### Getting a list of the candidate countries

countries = ["Afghanistan", "Haiti", "Lebanon"]

### Preprocessing
xs = {}
ys = {}
Ns = {}

for country in countries:
    ys[country] = ["Safety", "Participation", "Empowerment"]
    xs[country] = np.random.uniform(1, 6, 3)
    Ns[country] = np.random.choice(np.arange(500, 1001))

### Adding convenience variables

annot_font = dict(family="Arial, sans-serif", size=15,
                  color='#212F3D')

color_legend = False

Nfont = dict(family="Arial, sans-serif", size=18, color='black')

bar_width = 0.6

### Update menu
buttons = []
for country in countries:
    option = dict(
        args=[
            dict(
                x=[xs[country]],
                y=[ys[country]]
            ),
            dict(
                annotations=[dict(
                    text=str(Ns[country]),
                    font=Nfont,
                    showarrow=False,
                    xref='paper', x=0.95,
                    yref='paper', y=1)]
            )],
        label=country,
        method='update'
    )
    buttons.append(option)

updatemenus = list([
    dict(
        buttons=list(buttons
                     ),
        direction='down',
        pad={'r': 10, 't': 10},
        showactive=True,
        x=0,
        xanchor='left',
        y=1.1,
        yanchor='top'
    ),
])

### axis parameters
xaxis = dict(
    autorange=True,
    showgrid=False,
    zeroline=True,
    showline=False,
    ticks='',
    showticklabels=False
)

yaxis = dict(
    automargin=True,
    ticks='outside',
    ticklen=8,
    tickwidth=4,
    tickcolor='#FFFFFF',
    tickfont=dict(
        family="Arial, sans-serif",
        size=15,
        color='black'))

### trace
trace = (go.Bar(y=ys["Afghanistan"], x=xs["Afghanistan"],
                text=np.round(xs["Afghanistan"], 2), textposition='inside',
                name="Mean Satisfaction", marker=dict(color='#03CEA3'),
                orientation="h", showlegend=color_legend,
                textfont=annot_font, hoverinfo="name + text",
                width=bar_width))

### layout 
layout = go.Layout(barmode="stack",
                   xaxis=xaxis,
                   yaxis=yaxis,
                   annotations=[dict(text=str(Ns["Afghanistan"]),
                                     font=Nfont,
                                     showarrow=False,
                                     xref='paper', x=0.95,
                                     yref='paper', y=1)],
                   updatemenus=updatemenus)

fig = go.Figure(data=[trace], layout=layout)
fig.show()



