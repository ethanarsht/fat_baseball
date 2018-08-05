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
import seaborn as sns
#%%
df_data = pd.read_csv('~/fat_baseball/full_data.csv', index_col = 0)
df_data.reset_index(drop = True, inplace = True)
#%%
len(df_data)
#%%
df_data['last_year'] = np.nan
for i, row in df_data.iterrows():
    print(row['name'])
    if i == len(df_data) - 1:
        df_data.loc[i, 'last_year'] = 'yes'
    else:
        if row['name'] == df_data.loc[i+1, 'name']:
            df_data.loc[i, 'last_year'] = 'no'
        else:
            df_data.loc[i, 'last_year'] = 'yes'
        
#%%
df_data.columns
#%%
df_data.last_year.replace({'no':0, 'yes': 1}, inplace = True)
rpsp_dum = pd.get_dummies(df_data.starter)
X = pd.concat([df_data[['games', 'war', 'bmi', 'yoc']], rpsp_dum], axis = 1)
y = df_data.last_year
#%%
y.value_counts()[0] / len(df_data)
#%%
lr = LogisticRegression()
lr.fit(X,y)
lr.score(X, y)
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








