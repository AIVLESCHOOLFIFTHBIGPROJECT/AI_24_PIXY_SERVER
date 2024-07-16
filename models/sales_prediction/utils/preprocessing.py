import pandas as pd

def preprocessing(df):
    df.drop(columns='Unnamed: 0', axis=1, inplace=True)
    df=pd.get_dummies(df, columns=['family'])
    # df.set_index('date')
    return df