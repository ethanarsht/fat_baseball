#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 16:26:56 2018

@author: ethanarsht
"""
#%%
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import roc_curve, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
#%%
df_data = pd.read_csv('~/fat_baseball/full_data.csv', index_col = 0)
df_data.reset_index(drop = True, inplace = True)
#%%
df_active = pd.read_csv('~/fat_baseball/active_pitcher_data.csv', index_col = 0)
df_active.reset_index(drop = True, inplace = True)
df_active.gs = df_active.gs.replace('\xa0', 0)
df_active = df_active.drop_duplicates(subset = ['name','year'], keep = 'first').reset_index(drop = True)

#%%
df_active.gs = pd.to_numeric(df_active.gs)
#%%
df_active['starter'] = np.where(df_active['gs'] / df_active['games'] >= 0.5, 'sp', 'rp')
#%%
len(df_data)
#%%
def cleaner(df):
    df['last_year'] = np.nan
    for i, row in df.iterrows():
        print(row['name'])
        if i == len(df) - 1:
            df.loc[i, 'last_year'] = 'yes'
        else:
            if row['name'] == df.loc[i+1, 'name']:
                df.loc[i, 'last_year'] = 'no'
            else:
                df.loc[i, 'last_year'] = 'yes'
    
    df.last_year.replace({'no':0, 'yes': 1}, inplace = True)
    rpsp_dum = pd.get_dummies(df.starter)
    X = pd.concat([df[['games', 'war', 'bmi', 'yoc']], rpsp_dum], axis = 1)
    y = df.last_year
    return X, y

#%%
#cleaner(df_active)
X,y = cleaner(df_data)
Xa,ya = cleaner(df_active)
#%%
y.value_counts()[0] / len(df_data)
#%%
lr = LogisticRegression(class_weight = 'balanced')
lr.fit(X,y)
lr.score(X, y)
lr_preds = lr.predict(X)
#%%
X['intercept'] = 1.0
logit = sm.Logit(y, X)
result = logit.fit()
#%%
print(result.summary())
#%%
X_w = X.drop('bmi', axis = 1)
X_w = pd.concat([X_w, df_data['weight']], axis = 1)
#%%
logit = sm.Logit(y, X_w)
result = logit.fit()
print(result.summary())

#%%
sns.heatmap(df_data.corr())
#%%
X.drop('intercept', axis = 1, inplace = True)
rfc = RandomForestClassifier(class_weight = 'balanced')
rfc.fit(X, y)
#%%
rfc.score(X, y)

predictions = rfc.predict(X)
rfc_preds = pd.concat([y, pd.Series(predictions)], axis = 1)
#%%
print('Logistic regression cross-val-score:', np.mean(cross_val_score(lr, X, y, cv = 5, scoring = 'f1')))
print('Random forest cross-val-score:', np.mean(cross_val_score(rfc, X, y, cv = 5, scoring = 'f1')))
#%%
from sklearn.dummy import DummyClassifier
dc = DummyClassifier(strategy = 'stratified')
dc.fit(X,y)
dc.score(X,y)

#%%
lr_probs = cross_val_predict(lr, X, y, cv = 5, method = 'predict_proba')[:, 1]
rf_probs = cross_val_predict(rfc, X, y, cv = 5, method = 'predict_proba')[:, 1]
false_positive_rate, true_positive_rate, threshold = roc_curve(y, lr_probs)
rf_fp, rf_tp, rf_thresh = roc_curve(y, rf_probs)
#%%
plt.title('AUC Curve')
plt.plot(false_positive_rate, true_positive_rate, label = 'LogReg')
plt.plot(rf_fp, rf_tp, label = 'RandomForest')
plt.legend()
plt.plot([0,1], ls = "--")
plt.plot([0,0], [1,0], c = ".7"), plt.plot([1,1], c=".7")

#%%
lr_preds = lr.predict(X)
matrix = confusion_matrix(lr_preds, y)
df_cm = pd.DataFrame(matrix, index = [0,1], columns = [0,1])
sns.heatmap(df_cm, annot = True, cbar = None, cmap = "Blues")

#%%
active_pitcher_preds = lr.predict_proba(Xa)
df_ap = pd.concat([df_active[['name', 'year',]], pd.DataFrame(active_pitcher_preds)], axis = 1)
#%%

df_thisyear = df_ap[df_ap.year == 2018]
#%%









