import plotly.graph_objects as go
import pandas as pd
df = pd.read_csv("ircam_accuracies.csv")
df = df.sort_values(by=['accuracy'])
x = df['genre'].tolist()
y = df['accuracy'].tolist()
z = df['coverage'].tolist()

# Use the hovertext kw argument for hover text
fig = go.Figure(data=[go.Bar(name = "Accuracy",x=x, y=y,text = y,textposition='auto'),
                      go.Bar(name = "Coverage",x=x,y=z, text=z, textposition='auto')])
            # hovertext=['27% market share', '24% market share', '19% market share'])])
# Customize aspect
fig.update_traces(#marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
fig.update_layout(barmode="group",title_text='October 15 2019 IRCAM Genre Accuracy')
fig.update_yaxes(nticks=20)
fig.show()