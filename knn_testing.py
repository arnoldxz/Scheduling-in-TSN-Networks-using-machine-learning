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
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

# %%
filepath="F1.csv"
df, X, y, df_o, scaler = DataFrameHelper.X_y(filepath)
# %%
# Grid
k_range = list(range(1, 30))
model = KNeighborsClassifier(metric="euclidean")
param_grid = dict(n_neighbors=k_range)
# %%
# LOOCV
loo = GridSearchCV(model, param_grid, cv=LeaveOneOut())
loo.fit(X, y)
# DataFrameHelper.save(loo, "0.KNN_LOO_SC2")
# loo=load("KNN_LOO_2023-07-04_21-48-21.joblib")
# %%
# %%
# Classification report
y_pred_loo = loo.predict(X)
report_loo = classification_report(y, y_pred_loo)
print(report_loo)
# %%
# Wrong classified
wrong_loo = DataFrameHelper.get_wrong_classified(filepath, X, y, y_pred_loo)
# wrong_kfold = DataFrameHelper.get_wrong_classified(filepath, X, y, y_pred_kfold)
# %%
# Plot
fig_loo = ScatterPlot3D.scatter_plot_3d(df_o)
fig_loo.add_trace(go.Scatter3d(
    x=wrong_loo['T1'],
    y=wrong_loo['T2'],
    z=wrong_loo['T3'],
    mode='markers',
    marker=dict(
        size=10,
        color='yellow',
        opacity=0.35
    ),
    name='Wrong classified'
))
fig_loo.show()
# %%
# Best predictors
print(loo.best_estimator_)
