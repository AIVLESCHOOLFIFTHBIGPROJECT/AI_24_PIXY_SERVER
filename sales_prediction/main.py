import argparse
from models.train import train_model
from models.predict import predict_model
import pandas as pd
import torch

def parse_arguments():
    parser = argparse.ArgumentParser(description="Machine Learning Model Training and Evaluation Script")
    parser.add_argument("--runtype", type=str, required=True, choices=['train', 'predict'])
    parser.add_argument("--path", type=str, required=True)
    return parser.parse_args()

def main(runtype, path):
    data=pd.read_csv(path)

    if runtype=='train':
        model=train_model(data)
    elif runtype=='predict':
        prediction=predict_model(data)
        print(prediction)

        #필요에따라 출력 바꾸면 됨




if __name__ == "__main__":
    args = parse_arguments()
    main(args.runtype, args.path)