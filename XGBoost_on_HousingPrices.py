# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 14:02:39 2023

@author: Yigitalp
"""
# Import the libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

# Import the train data
df_train = pd.read_csv('train.csv')

# Dataset information
df_train.info()
df_train_describe = df_train.describe()
sum_isna_train = df_train.isna().sum()

# Drop columns with missing values
for col in df_train.columns:
    if df_train[col].isna().sum() >= 1:
        df_train = df_train.drop(col, axis=1)

# Split categorical variables
df_train = pd.get_dummies(df_train)

# Features
features = [col for col in df_train.columns if col not in ['Id', 'SalePrice']]

# Correlation & Feature selection
correlation = abs(df_train[features].corrwith(df_train['SalePrice']))
correlation.name = 'Corr Scores'
selected_features = [
    idx for idx in correlation.index if correlation.loc[idx] >= 0.005]

# Split train and test
X = df_train[selected_features]
y = df_train['SalePrice']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.8, test_size=0.2, random_state=0)

# Train the xgbregression model on train set
xgb = XGBRegressor(learning_rate=0.01, n_estimators=3460,
                   max_depth=3, min_child_weight=0,
                   gamma=0, subsample=0.7,
                   colsample_bytree=0.7,
                   objective='reg:squarederror', nthread=-1,
                   scale_pos_weight=1, seed=27,
                   reg_alpha=0.00006)

xgb.fit(X_train, y_train)

y_pred_xgb = xgb.predict(X_test)

# Calculate accuracy score xgbregression
test_mae_xgb = mean_absolute_error(y_pred_xgb, y_test)
#%%

# Predict full data xgbregression model
xgb_full_data = XGBRegressor(learning_rate=0.01, n_estimators=3460,
                             max_depth=3, min_child_weight=0,
                             gamma=0, subsample=0.7,
                             colsample_bytree=0.7,
                             objective='reg:squarederror', nthread=-1,
                             scale_pos_weight=1, seed=27,
                             reg_alpha=0.00006)

# Remove some missing columns according to test set
selected_features_test = [col for col in selected_features if col not in ['Utilities_NoSeWa', 'Condition2_RRAn', 'Condition2_RRNn', 'HouseStyle_2.5Fin',
                                                                          'RoofMatl_ClyTile', 'RoofMatl_Membran', 'RoofMatl_Roll', 'Exterior1st_ImStucc', 'Exterior1st_Stone', 'Exterior2nd_Other', 'Heating_Floor', 'Heating_OthW']]

# Fit full data based on selected features according to test data
xgb_full_data.fit(X[selected_features_test], y)

# Import the test data
df_test = pd.read_csv('test.csv')

# Dataset information
df_test.info()
df_test_describe = df_test.describe()

# Split categorical variables
df_test = pd.get_dummies(df_test)

# assing selected features according to test data
test_X = df_test[selected_features_test]

# Fill missing values
for col in test_X.columns:
    if test_X[col].isna().sum() >= 1:
        test_X[col] = test_X[col].fillna(test_X[col].mode()[0])

# Predict test set
test_preds_xgb = xgb_full_data.predict(test_X)

# Create submission csv
submission = pd.DataFrame({
    'Id': df_test['Id'],
    'SalePrice': test_preds_xgb
})

submission.to_csv('submission.csv', index=False)
