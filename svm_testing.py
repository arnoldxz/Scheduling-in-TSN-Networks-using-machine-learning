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
from helper import ScatterPlot3D
# %%
filepath="SC1-0.csv"
df, X, y, df_o, scaler = DataFrameHelper.X_y(filepath)
# %%
c_range = np.arange(0.1, 50, 1)
gamma_range = np.logspace(-9, 3, 13) 
param_grid = {'C': c_range, 'gamma': gamma_range, 'kernel': ['rbf']}
# %%
# LOOCV
loo = GridSearchCV(SVC(), param_grid, cv=LeaveOneOut())
loo.fit(X, y)
# DataFrameHelper.save(loo, "0.SVM_LOO_rbf_E")
# loo=load("SVM_LOO_2023-07-04_21-14-46.joblib")
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
