import os
import pandas as pd
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump
import dvc.api
from dvclive.lightning import DVCLiveLogger

dvc_params = dvc.api.params_show()
train_params=dvc_params["train"]
n_neighbors=train_params["n_neighbors"]

dev_train = pd.read_csv("./data/train_resampled.csv")
label_train = pd.read_csv("./data/train_label_resampled.csv")
label_train = label_train["class"]

# KNN
start = datetime.now()
print("Train Start:", start)

neigh = KNeighborsClassifier(n_neighbors=n_neighbors, logger=DVCLiveLogger(save_dvc_exp=True)) #add best parameters
neigh.fit(dev_train, label_train)

end = datetime.now()
print("Train End:", end)
print(end -start)

if not os.path.exists("./model"):
   os.makedirs("./model")

dump(neigh, './model/model.joblib') 