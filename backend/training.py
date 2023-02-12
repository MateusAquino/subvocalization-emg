from brainflow.board_shim import BoardIds
from backend.cyton_stream import preprocess
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from keras.callbacks import Callback
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout
from keras.utils import to_categorical
import pandas as pd
import random as rd
import numpy as np
import string
import eel


def train_data(file_name, ratio, recordings, batch_size, epochs):
    if not file_name:
        file_name = ''.join(rd.choice(string.ascii_uppercase)
                            for i in range(10))
    eel.log("Start new network (%s) training" % (file_name))
    emg_words = []
    emg_data = []
    columns = ['Channel_{}'.format(x) for x in range(1, 9)]

    for save in recordings:
        restored_df = pd.read_csv("dist/saves/%s.csv" % (save))
        x = preprocess(restored_df, BoardIds.CYTON_BOARD, columns)
        preprocessed_data = np.transpose(x)
        word = None
        data = None
        for i in range(len(restored_df)):
            if i == 0:
                word = restored_df.iloc[i, 0]
                data = preprocessed_data[i]
            elif restored_df.iloc[i, 0] == word:
                data = np.vstack((data, preprocessed_data[i]))
            else:
                emg_words.append(word)
                emg_data.append(data)
                word = restored_df.iloc[i, 0]
                data = preprocessed_data[i]

        emg_words.append(word)
        emg_data.append(data)

    # Plot words
    # plt.figure()
    # _f, axarr = plt.subplots(1, len(emg_words), constrained_layout=True)
    # for i, word in enumerate(emg_words):
    #   axarr[i].imshow(emg_data[i], cmap='hot', interpolation='none')
    #   axarr[i].title.set_text(word)
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
              activation='relu', input_shape=(samples, 8)))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(3))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(50, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(possibilities, activation='softmax'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])

    model.fit(X_train, y_train, validation_data=(
        X_test, y_test), batch_size=batch_size,
        epochs=epochs, verbose=0, callbacks=[ProgressCallback()], shuffle=True)

    # Save network + words (answers) + sampling rate
    model.save("dist/networks/%s" % (file_name))
    pd.DataFrame(words_map, columns=["Word"]).to_csv(
        "dist/networks/%s/words.csv" % (file_name))
    f = open("dist/networks/%s/samples" % (file_name), "w")
    f.write(samples)
    f.close()
    eel.sync_files()


class ProgressCallback(Callback):
    def on_test_end(self, logs=None):
        eel.train_progress("train", logs['loss'], logs['accuracy'])

    def on_epoch_end(self, epoch, logs=None):
        eel.train_progress(
            epoch, logs['loss'], logs['accuracy'], logs['val_loss'], logs['val_accuracy'])
