from backend.cyton_stream import get_current_board_data, preprocess, set_save_resources
from brainflow.board_shim import BoardShim, BoardIds
from tensorflow import keras
import pandas as pd
import numpy as np
import eel

predicting = False


def predict_emg(network_id, history_count, refresh_rate):
    global predicting
    predicting = True
    set_save_resources(True)
    model = keras.models.load_model("dist/networks/%s" % (network_id))
    words = pd.read_csv("dist/networks/%s/words.csv" % (network_id))
    f = open("dist/networks/%s/samples" % (network_id), "r")
    sampling_rate = int(f.read())
    exg_channels = BoardShim.get_exg_channels(BoardIds.CYTON_BOARD)
    last_predictions = []
    while (predicting):
        emg_data = get_current_board_data(sampling_rate)
        emg_data = preprocess(emg_data, BoardIds.CYTON_BOARD, exg_channels)
        emg_data = np.transpose(emg_data).astype('float32')
        emg_data = np.expand_dims(emg_data, axis=0)
        prediction = model.predict(emg_data, verbose=0)
        prediction = np.argmax(prediction, axis=1)
        prediction = words.iloc[prediction].values[0][1]
        last_predictions.append(prediction)
        if len(last_predictions) > history_count:
            last_predictions.pop(0)
        most_seen = max(set(last_predictions), key=last_predictions.count)
        eel.update_prediction(most_seen, last_predictions)
        eel.sleep(refresh_rate)
    set_save_resources(False)


def stop_predicting_stream():
    global predicting
    predicting = False
