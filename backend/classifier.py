from backend.cyton_stream import get_current_board_data, preprocess, get_exg_channels, get_board_id
from brainflow.board_shim import BoardIds
from tensorflow import keras
import pandas as pd
import numpy as np
import eel

predicting = False


def predict_emg(network_id, history_count, refresh_rate):
    global predicting
    predicting = True
    exg_channels = get_exg_channels()
    board_id = get_board_id()
    model = keras.models.load_model("dist/networks/%s" % (network_id))
    words = pd.read_csv("dist/networks/%s/words.csv" % (network_id))
    f = open("dist/networks/%s/samples" % (network_id), "r")
    sampling_rate = int(f.read())
    f.close()
    f = open("dist/networks/%s/channels" % (network_id), "r")
    channels = int(f.read())
    f.close()
    last_predictions = []
    while (predicting):
        emg_data = get_current_board_data(sampling_rate*5)[exg_channels]
        emg_data = np.array(emg_data)
        emg_data = preprocess(emg_data, board_id, [*range(len(exg_channels))])[:channels,-sampling_rate:]
        emg_data = np.transpose(emg_data)
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


def stop_predicting_stream():
    global predicting
    predicting = False
