import pickle

def predict_model(data):
    with open('./data/saved_model.pickle', 'rb') as f:
        model=pickle.load()
    return model.predict(data)
