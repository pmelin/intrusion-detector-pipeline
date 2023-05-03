import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter
import dvc.api

dvc_params = dvc.api.params_show()
prepare_params=dvc_params["prepare"]
test_size=prepare_params["test_size"]
sampling_strategy=prepare_params["sampling_strategy"]

dev = pd.read_csv("./data/dev.csv")

#exclude in dev attributes without variation
dev = dev.loc[:, (dev != dev.iloc[0]).any()]

#Transform nominal values in features
x_dev = pd.get_dummies(dev).drop('class', axis=1)
y_dev = dev["class"]  # Target variable

# Drop not used collumns
x_dev = x_dev.drop('service_red_i', axis=1)
x_dev = x_dev.drop('service_pm_dump', axis=1)
x_dev = x_dev.drop('service_tftp_u', axis=1)

cols_dev = x_dev.columns
scaler = MinMaxScaler()
scaler.fit(x_dev)
x_dev = scaler.transform(x_dev)
x_dev = pd.DataFrame(x_dev, columns=cols_dev)

## Split dataset into training set and test set
dev_train, dev_test, label_train, label_test = train_test_split(x_dev, y_dev, test_size=test_size, stratify=y_dev)
# 70% training and 30% test

dev_test.to_csv('./data/test_prepared.csv', index=False)
label_test.to_csv('./data/test_label.csv', index=False)

dev_train.to_csv('./data/train_prepared.csv', index=False)
label_train.to_csv('./data/train_label.csv', index=False)

