import pandas as pd
from joblib import dump, load
from sklearn import preprocessing
from datetime import datetime

class DataFrameHelper:
    @staticmethod
    def scale(df):
        scaler = preprocessing.StandardScaler()
        df.iloc[:, :-1] = scaler.fit_transform(df.iloc[:, :-1])
        df.iloc[:, -1] = df.iloc[:, -1].astype(int)
        return df, scaler

    @staticmethod
    def X_y(filepath, selected_cols=['T1', 'T2', 'T3', 'Feasibility']):
        df = pd.read_csv(filepath)
        df_original = pd.read_csv(filepath)
        df = df[selected_cols]

        scaler = preprocessing.StandardScaler()
        df.iloc[:, :-1] = scaler.fit_transform(df.iloc[:, :-1])
        df.iloc[:, -1] = df.iloc[:, -1].astype(int)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]

        return df, X, y, df_original, scaler
    
    @staticmethod
    def save(model, name=""):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        dump(model, f"{name}_{timestamp}.joblib")
    
    @staticmethod
    def get_wrong_classified(filepath, X, y, y_pred):
        df_wrong_indexs = X[y != y_pred]
        dfo = pd.read_csv(filepath)

        wrong_indexs = df_wrong_indexs.index
        df_wrong = dfo.iloc[wrong_indexs]

        return df_wrong