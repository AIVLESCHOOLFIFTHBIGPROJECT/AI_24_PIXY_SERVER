import pickle

def predict_model(data):
    data = data.set_index('date')
    with open('../../media/weight/saved_model.pickle', 'rb') as f:
        model=pickle.load(f)
    return model.predict(data)
