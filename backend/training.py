import tensorflow as tf

gpu_devices = tf.config.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)

from brainflow.board_shim import BoardIds
from backend.cyton_stream import preprocess
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from keras.callbacks import Callback, ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import LSTM, Conv1D, MaxPooling1D, GlobalAveragePooling1D, Normalization, Flatten, Dense, Dropout, BatchNormalization
from keras.utils import to_categorical
from keras import regularizers
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
import random as rd
import numpy as np
import string
import eel


def train_data(network_id, ratio, recordings, batch_size, epochs, channels, window_size):
    if not network_id:
        network_id = ''.join(rd.choice(string.ascii_uppercase)
                             for i in range(10))
    eel.log("Start new network (%s) training" % (network_id))
    
    words_map, samples, model, _history, _report = train_network(ratio, recordings, batch_size, epochs, channels, window_size, [ProgressCallback()])

    # Save network + words (answers) + sampling rate
    model.save("dist/networks/%s" % (network_id))
    pd.DataFrame(words_map, columns=["Word"]).to_csv(
        "dist/networks/%s/words.csv" % (network_id))
    f = open("dist/networks/%s/samples" % (network_id), "w")
    f.write("%s" % (samples))
    f.close()
    f = open("dist/networks/%s/channels" % (network_id), "w")
    f.write("%s" % (channels))
    f.close()
    eel.sync_files()

def train_network(ratio, recordings, batch_size, epochs, channels, window_size, callbacks=[]):
  emg_words = []
  emg_data = []
  columns = ['Channel_{}'.format(x) for x in range(1, channels+1)]

  for save in recordings:
      restored_df = pd.read_csv("dist/saves/%s.csv" % (save))
      x = preprocess(restored_df, BoardIds.CYTON_BOARD, columns)[:,:channels]
      preprocessed_data = np.transpose(x)
      word = None
      data = None
      for i in range(len(restored_df)):
          if i == 0:
              word = restored_df.iloc[0, 0]
              data = preprocessed_data[:, 0]
          elif restored_df.iloc[i, 0] == word:
              data = np.vstack((data, preprocessed_data[:, i]))
          else:
              emg_words.append(word)
              emg_data.append(data)
              word = restored_df.iloc[i, 0]
              data = preprocessed_data[:, i]

      emg_words.append(word)
      emg_data.append(data)
  
  # Separate data into lower windows when one stream mode
  one_stream = save.endswith("_1S")
  if one_stream:
      emg_words, emg_data = separate_data(emg_words, emg_data, window_size)

  # Get minimum length of emg_data to make all data the same length
  len_array = [len(x) for x in emg_data]
  samples = min(len_array)
  max_samples = max(len_array)
  avg_samples = int(sum(len_array)/len(len_array))
  data_original = len(emg_data)
  
  # remove small samples if too small compared to average
  if avg_samples - samples > max_samples - avg_samples:
      # remove samples from emg_data and emg_words with length smaller than average
      emg_words = [word for i, word in enumerate(emg_words) if len(emg_data[i]) > avg_samples-12]
      emg_data = [data for data in emg_data if len(data) > avg_samples-12]

  len_array = [len(x) for x in emg_data]
  new_samples = min(len_array)
  new_avg_samples = int(sum(len_array)/len(len_array))
  data_reduced = [emg_data[-new_samples:] for emg_data in emg_data]
  len_reduced = len(data_reduced)

  print('Original words count:', data_original)
  print('Original Avg Samples (per word):', avg_samples)
  print('New words count:', len_reduced, "(removed", data_original - len_reduced, "words)")
  print('New Avg Samples (per word):', new_avg_samples)
  print('New Samples:', new_samples, "(removed", new_avg_samples - new_samples, "samples from average)")

  emg_data = np.asarray(data_reduced[1:]).astype('float32')
  # transform each unique string in emg_word array into a number
  emg_words, words_map = pd.factorize(emg_words[1:])
  emg_words = to_categorical(emg_words)
  possibilities = len(words_map)

  X_train, X_test, y_train, y_test = train_test_split(
      emg_data, emg_words, test_size=((100-ratio)/100.0))

  # Build Model
  model = Sequential()
  model.add(Normalization(axis=-1)) 
  model.add(Conv1D(50, 3, strides=1, activation='relu', 
                 kernel_regularizer=regularizers.l2(0.001), input_shape=(new_samples, channels)))
  model.add(BatchNormalization())
  model.add(Dropout(0.3))

  model.add(GlobalAveragePooling1D())
  model.add(Dense(40, activation='tanh', kernel_regularizer=regularizers.l2(0.001)))
  model.add(Dropout(0.3))

  model.add(Dense(possibilities, activation='softmax'))

  model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
  lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
  callbacks.append(lr_scheduler)

  history = model.fit(X_train, y_train, validation_data=(
        X_test, y_test), batch_size=batch_size,
        epochs=epochs, verbose=0, callbacks=callbacks, shuffle=True)

  y_pred = np.asarray([np.argmax(model.predict(np.expand_dims(x, axis=0), verbose=0), axis=1) for x in X_test])
  report = classification_report(np.argmax(y_test, axis=1), y_pred.flatten(), target_names=words_map) 

  return words_map, new_samples, model, history, report

def separate_data(emg_words, emg_data, window_size):
    new_words = []
    new_data = []
    for i in range(len(emg_words)):
        word = emg_words[i]
        data = emg_data[i]
        for j in range(0, len(data), window_size):
            new_words.append(word)
            new_data.append(data[j:j+window_size])
    return new_words, new_data

class ProgressCallback(Callback):
    def on_test_end(self, logs=None):
        eel.train_progress("train", logs['loss'], logs['accuracy'])

    def on_epoch_end(self, epoch, logs=None):
        eel.train_progress(
            epoch, logs['loss'], logs['accuracy'], logs['val_loss'], logs['val_accuracy'])
