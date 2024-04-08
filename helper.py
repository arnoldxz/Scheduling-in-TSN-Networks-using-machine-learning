import plotly.graph_objects as go
import pandas as pd

class ScatterPlot3D:
    @staticmethod
    def scatter_plot_3d(df):

        if 'Exceeds_Bw' not in df.columns:
            df.insert(loc=len(df.columns), column='Exceeds_Bw', value=False)

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
    
    @staticmethod
    def add_wrong_instance_trace(fig, df_wrong):
        fig.add_trace(go.Scatter3d(
            x=df_wrong['T1'],
            y=df_wrong['T2'],
            z=df_wrong['T3'],
            mode='markers',
            marker=dict(
                size=10,
                color='yellow',
                opacity=0.35
            ),
            name='Wrong classified'
        ))
        return fig

class CombinationPredictor:
    @staticmethod
    def combinations(m=15):
        x = 0
        y = 0
        z = 0

        df_res = pd.DataFrame(columns=['T1', 'T2', 'T3', 'Feasibility'])
        for i in range(m+1):
            for j in range(m+1):
                for k in range(m+1):
                    if i + j + k == m:
                        df_res = pd.concat([df_res, pd.DataFrame([[i, j, k, 0]], columns=['T1', 'T2', 'T3', 'Feasibility'])])

        df_res = df_res.reset_index(drop=True)
        return df_res

    @staticmethod
    def predict_all(dfx, model):
        for index, row in dfx.iterrows():
            pred = model.predict([[row['T1'], row['T2'], row['T3']]])
            dfx.at[index, 'Feasibility'] = pred[0]
        return dfx
