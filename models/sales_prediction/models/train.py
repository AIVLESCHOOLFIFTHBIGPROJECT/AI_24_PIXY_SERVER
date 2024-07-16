import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import *
from sklearn.preprocessing import MinMaxScaler

from sklearn.ensemble import RandomForestRegressor

import pickle

global_fig_settings = {
    'renderer': 'png',
    'width': 1000,
    'height': 600,
}

def pred_plot(y_val, pred, date, title):
    plt.figure(figsize = (18,6))
    sns.lineplot(x=date, y = y_val.values, label = 'actual value', marker = 'o')
    sns.lineplot(x=date, y = pred, label = 'predicted value', marker = 'o')
    plt.grid()
    plt.title(f"{title}", fontsize = 16)
    plt.ylabel('Sales', fontsize = 14)
    plt.xlabel('Date', fontsize = 14)
    plt.show()

def train_model(df):
    df1 = df.set_index('date')
    x = df1.drop(['sales'], axis = 1)
    y = df1['sales']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, shuffle = False, random_state = 1)
    print(x_train.shape, x_test.shape)

    RF  = RandomForestRegressor(random_state = 42)

    param = {'max_depth': range(1, 51)}

    model = RandomizedSearchCV(RF,     #기본 모델
                            param,   #파라미터 범위
                            cv = 5,  # K-Fold 개수
                            n_iter = 20, # 선택할 잉의 파라미터 개수
                            scoring = 'r2')
    
    model.fit(x_train, y_train)

    # 중요 정보 확인
    print('=' * 80)
    print(model.cv_results_['mean_test_score'])
    print('-' * 80)
    print('최적파라미터:', model.best_params_)
    print('-' * 80)
    print('최고성능:', model.best_score_)
    print('=' * 80)

    MAE={}
    MAPE={}

    RF = RandomForestRegressor(max_depth = 5, n_estimators=200, random_state= 42)
    RF.fit(x_train, y_train)
    y_pred = RF.predict(x_test)
    print("r2: ", r2_score(y_test, y_pred))
    print("MAE: ", mean_absolute_error(y_test, y_pred))
    print("MAPE: ", mean_absolute_percentage_error(y_test, y_pred) )

    MAE['RF'] = mean_absolute_error(y_test, y_pred)
    MAPE['RF'] = mean_absolute_percentage_error(y_test, y_pred) 

    with open('../../media/weight/saved_model.pickle', 'wb') as f:
        pickle.dump(model, f)
