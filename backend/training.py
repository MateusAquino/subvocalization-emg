from brainflow.data_filter import DataFilter
import pandas as pd
import random as rd
import numpy as np
import string
import eel

def train_data(file_name, ratio, recordings):
  if not file_name:
      file_name = ''.join(rd.choice(string.ascii_uppercase) for i in range(10))
  eel.log("Start new network (%s) training" % (file_name))
  for save in recordings:
    restored_df = pd.read_csv("dist/saves/%s.csv" % (save)) 


  print(file_name)
  print(ratio)
  eel.sync_files()
