import os
import pandas as pd
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump
import dvc.api

dvc_params = dvc.api.params_show()
train_params=dvc_params["train"]
n_neighbors=train_params["n_neighbors"]

dev_train = pd.read_csv("./data/train_prepared.csv")
label_train = pd.read_csv("./data/train_label.csv")
label_train = label_train["class"]

# KNN

neigh = KNeighborsClassifier(n_neighbors=n_neighbors)
neigh.fit(dev_train, label_train)

if not os.path.exists("./model"):
   os.makedirs("./model")

dump(neigh, './model/model.joblib') 