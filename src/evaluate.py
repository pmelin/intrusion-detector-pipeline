import os
import pandas as pd
from dvclive import Live
from sklearn import metrics
from joblib import load
import json
import math

EVAL_PATH = "eval"

def evaluate(model, labels, x, split, live):

  predictions_by_class = model.predict_proba(x)
  predictions = predictions_by_class[:, 1]

  # Use dvclive to log a few simple metrics...
  avg_prec = metrics.average_precision_score(labels, predictions)
  roc_auc = metrics.roc_auc_score(labels, predictions)

  if not live.summary:
      live.summary = {"avg_prec": {}, "roc_auc": {}}
  
  live.summary["avg_prec"][split] = avg_prec
  live.summary["roc_auc"][split] = roc_auc

  live.log_sklearn_plot("roc", labels, predictions, name=f"roc/{split}")

  precision, recall, prc_thresholds = \
          metrics.precision_recall_curve(labels, predictions)
  nth_point = math.ceil(len(prc_thresholds) / 1000)
  prc_points = list(zip(precision, recall, prc_thresholds))[::nth_point]
  prc_dir = os.path.join(EVAL_PATH, "prc")
  os.makedirs(prc_dir, exist_ok=True)
  prc_file = os.path.join(prc_dir, f"{split}.json")
  with open(prc_file, "w") as fd:
      json.dump(
          {
              "prc": [
                  {"precision": p, "recall": r, "threshold": t}
                  for p, r, t in prc_points
              ]
          },
          fd,
          indent=4,
      )


  # ... confusion matrix plot
  live.log_sklearn_plot("confusion_matrix",
                        labels.squeeze(),
                        predictions_by_class.argmax(-1),
                        name=f"cm/{split}"
                        )

dev_train = pd.read_csv("./data/train_prepared.csv")
label_train = pd.read_csv("./data/train_label.csv")
label_train = label_train["class"]

dev_test = pd.read_csv("./data/test_prepared.csv")
label_test = pd.read_csv("./data/test_label.csv")
label_test = label_test["class"]

model = load('./model/model.joblib') 

# Evaluate train and test datasets.
live = Live(os.path.join(EVAL_PATH, "live"), dvcyaml=False)
evaluate(model, label_train, dev_train, "train", live)
evaluate(model, label_test, dev_test, "test", live)
live.make_summary()
