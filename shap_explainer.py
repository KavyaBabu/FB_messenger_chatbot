import numpy as np
from keras.models import load_model
from keras.utils import pad_sequences
import pickle
import shap

str = ["this is news"]
class_names=["fake","true"]

model = load_model('news_ChatBot.h5')

def predict_proba(str):
 
  with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

  str = tokenizer.texts_to_sequences(str);
  str = pad_sequences(str, maxlen=1000);
  result = model.predict(str);
  returnable=[]
  for i in result:
    temp=i[0]
    returnable.append(np.array([1-temp,temp]))
  return np.array(returnable)
