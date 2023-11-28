from brainflow.board_shim import BoardIds
from backend.cyton_stream import preprocess
from sklearn.model_selection import train_test_split
from keras.callbacks import Callback
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout
from keras.utils import to_categorical
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
    
    words_map, samples, model = train_network(ratio, recordings, batch_size, epochs, channels, window_size, [ProgressCallback()])

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
              word = restored_df.iloc[i, 0]
              data = preprocessed_data[:, i]
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

  # Plot words | Display data in Jupyter Notebook
  # plt.figure()
  # _f, axarr = plt.subplots(1, 4, constrained_layout=True, figsize=(6, 6))
  # for i, word in enumerate(emg_words[:4]):
  #     axarr[i].imshow(emg_data[i], cmap='hot', interpolation='none')
  #     axarr[i].title.set_text(word + ' %d'% (1 + i/5))
  #     axarr[i].set(xticks=[])
  # plt.show() 

  # Get minimum length of emg_data to make all data the same length
  samples = min([len(x) for x in emg_data])
  data_reduced = [x[:samples] for x in emg_data]

  emg_data = np.asarray(data_reduced).astype('float32')
  # transform each unique string in emg_word array into a number
  emg_words, words_map = pd.factorize(emg_words)
  emg_words = to_categorical(emg_words)
  possibilities = len(words_map)

  X_train, X_test, y_train, y_test = train_test_split(
      emg_data, emg_words, test_size=((100-ratio)/100.0))

  # Build Model
  model = Sequential()
  model.add(Conv1D(40, 10, strides=2, padding='same',
              activation='relu', input_shape=(samples, channels)))
  model.add(Dropout(0.2))
  model.add(MaxPooling1D(3))
  model.add(GlobalAveragePooling1D())
  model.add(Dense(50, activation='relu'))
  model.add(Dropout(0.2))
  model.add(Dense(possibilities, activation='softmax'))

  model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])

  history = model.fit(X_train, y_train, validation_data=(
        X_test, y_test), batch_size=batch_size,
        epochs=epochs, verbose=0, callbacks=callbacks, shuffle=True)

  return words_map, samples, model, history

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
