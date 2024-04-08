# %%
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from sklearn.svm import SVC
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold
from mlhelper import DataFrameHelper
from helper import ScatterPlot3D, CombinationPredictor
# %%
# CSV
filepath="F1.csv"
df, X, y, df_o, scaler = DataFrameHelper.X_y(filepath)
# %%
# GridSearch
c_range = np.arange(0.1, 50, 1)
gamma_range = np.logspace(-9, 3, 13) 
param_grid = {'C': c_range, 'gamma': gamma_range, 'kernel': ['rbf']}
# %%
# LOOCV
# loo = GridSearchCV(SVC(), param_grid, cv=LeaveOneOut())
# loo.fit(X, y)
# dump(loo, f"loo_base.joblib")
loo=load("loo_base.joblib")
# %%
# Classification report
y_pred_loo = loo.predict(X)
report_loo = classification_report(y, y_pred_loo)
print(report_loo)
# %%
#Support vectors
svm = loo.best_estimator_
support_vector_indices = np.where(np.isin(X, svm.support_vectors_).all(axis=1))[0]
support_vectors = df_o.loc[support_vector_indices].to_numpy()
support_vectors
# %%
# predict all combinations
def combinations(m=15):
    x = 0
    y = 0
    z = 0

    df_res = pd.DataFrame(columns=['T1', 'T2', 'T3', 'Feasibility'])
    # add to dictionary d every combination of x, y, z so that the sum of the values is 20
    for i in range(m+1):
        for j in range(m+1):
            for k in range(m+1):
                if i + j + k == m:
                    # pred = model.predict([[i, j, k]])
                    # df_res=df_res.append({'T1': i, 'T2': j, 'T3': k, 'Feasibility': None}, ignore_index=True)
                    # use pandas concat instead of append
                    df_res = pd.concat([df_res, pd.DataFrame([[i, j, k, 0]], columns=['T1', 'T2', 'T3', 'Feasibility'])])
    # set index to df_res
    df_res = df_res.reset_index(drop=True)
    return df_res
def predict_all(dfx, model):
    for index, row in dfx.iterrows():
        pred = model.predict([[row['T1'], row['T2'], row['T3']]])
        dfx.at[index, 'Feasibility'] = pred[0]
    return dfx
dfc10 = combinations(10)
dfc12 = combinations(12)
dfc_t = pd.concat([dfc10, dfc12], ignore_index=True)
dfc_t_scaled = scaler.transform(dfc_t.iloc[:, :-1])
dfc_t_scaled = pd.concat([pd.DataFrame(dfc_t_scaled), dfc_t.iloc[:, -1]],axis=1)
dfc_t_scaled.columns = dfc_t.columns
# %%
df_res = predict_all(dfc_t_scaled, loo)
df_res_unscaled = pd.DataFrame(np.round(scaler.inverse_transform(df_res.iloc[:, :-1])), columns=df_res.columns[:-1])
df_res_unscaled = pd.concat([df_res_unscaled, df_res['Feasibility']], axis=1)
df_res_unscaled = df_res_unscaled.astype(int)
df_res_unscaled['Feasibility'] = df_res_unscaled['Feasibility'].astype(bool)
df_res_unscaled_10 = df_res_unscaled[df_res_unscaled['T1'] + df_res_unscaled['T2'] + df_res_unscaled['T3'] == 10]
df_res_unscaled_12 = df_res_unscaled[df_res_unscaled['T1'] + df_res_unscaled['T2'] + df_res_unscaled['T3'] == 12]
# %%
# compare with all combinations
df_complete = pd.read_csv('F_Total.csv')
merge = pd.merge(df_complete, df_res_unscaled, on=['T1', 'T2', 'T3'], how='inner')
merge = merge.rename(columns={'Feasibility_x': 'Feasibility_real', 'Feasibility_y': 'Feasibility_predicted'})
# wrong predicted values
df_wrong = merge[merge['Feasibility_real'] != merge['Feasibility_predicted']]
print("Number of wrong predictions: {}/{}".format(len(df_wrong), len(merge)))
print("Percentage of wrong predictions: {}".format(len(df_wrong)/len(merge)))
df_wrong
# %%
# missing data
df_o_o = df_o[['T1', 'T2', 'T3', 'Feasibility']]
merged_df = pd.merge(df_complete, df_o_o, how='outer', indicator=True)
missing_data_df = merged_df[merged_df['_merge'] == 'left_only']
missing_data_df = missing_data_df.drop('_merge', axis=1)
missing_data_df = missing_data_df[['T1', 'T2', 'T3', 'Feasibility']]
missing_data_df
# %%
# plot missing data and wrong predicted
fig_loo = ScatterPlot3D.scatter_plot_3d(missing_data_df)
fig_loo.add_trace(go.Scatter3d(
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
# %%
# additional data
df_additional = pd.read_csv("F.additional_data.csv")
fig_loo = ScatterPlot3D.scatter_plot_3d(missing_data_df)
fig_loo.add_trace(go.Scatter3d(
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
fig_loo.add_trace(go.Scatter3d(
    x=df_additional['T1'],
    y=df_additional['T2'],
    z=df_additional['T3'],
    mode='markers',
    marker=dict(
        size=10,
        color='cyan',
        opacity=1,
        symbol='circle-open' 
    ),
    name='Additional'
))
