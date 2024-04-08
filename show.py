# %%
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config_provider import ConfigService

configService = ConfigService() 
config = configService.config

filename = config["results_filename"]
n_streams = configService.networkConfig["n_streams"]
base_path = config["base_path"]

PATH = f"{base_path}\\{n_streams}\\{filename}"

def scatter_plot_3d(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=df[df['Feasibility'] == True]['T1'],
        y=df[df['Feasibility'] == True]['T2'],
        z=df[df['Feasibility'] == True]['T3'],
        mode='markers',
        marker=dict(
            size=5,
            color='#0C4B8E',
            opacity=0.8

        ),
        name='Feasible'
    ))

    fig.add_trace(go.Scatter3d(
        x=df[df['Feasibility'] == False]['T1'],
        y=df[df['Feasibility'] == False]['T2'],
        z=df[df['Feasibility'] == False]['T3'],
        mode='markers',
        marker=dict(
            size=5,
            color='#BF382A',
            opacity=0.8
        ),
        name='Not Feasible'
    ))

    fig.add_trace(go.Scatter3d(
        x=df[df['Exceeds_Bw'] == True]['T1'],
        y=df[df['Exceeds_Bw'] == True]['T2'],
        z=df[df['Exceeds_Bw'] == True]['T3'],
        mode='markers',
        marker=dict(
            size=10,
            color='#800080',
            opacity=0.5
        ),
        name='Exceeds Bw'
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='T1',
            yaxis_title='T2',
            zaxis_title='T3'
        ),
        width=750,
        height=750
    )

    return fig