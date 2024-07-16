import argparse
from models.train import train_model
from models.predict import predict_model
from utils.preprocessing import preprocessing
import pandas as pd
import torch

import boto3
import os
import glob

path='../../media/store'
files = glob.glob(os.path.join(path, '*'))
if files:
    # 파일들을 수정 시간 기준으로 정렬합니다.
    latest_file = max(files, key=os.path.getmtime)
    
    print(f"가장 최근에 수정된 파일: {latest_file}")
else:
    print("폴더가 비어있습니다.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Machine Learning Model Training and Evaluation Script")
    parser.add_argument("--runtype", type=str, required=True, choices=['train', 'predict'])
    return parser.parse_args()

def main(runtype):
    data=pd.read_csv(latest_file)
    data=preprocessing(data)
    if runtype=='train':
        model=train_model(data)
    elif runtype=='predict':
        prediction=predict_model(data)
        print(prediction)
        #필요에따라 출력 바꾸면 됨




if __name__ == "__main__":
    args = parse_arguments()
    main(args.runtype)