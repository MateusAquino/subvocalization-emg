from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations, NoiseTypes, AggOperations
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import numpy as np
import logging
import eel

running = False
save_resources = False
board = None
board_id = BoardIds.SYNTHETIC_BOARD
exg_channels = None
sampling_rate = None


def is_session_running():
    return running


def stop_stream():
    global running
    if board != None:
        running = False


def start_stream(port=''):
    try:
        eel.state("Starting")
        BoardShim.enable_dev_board_logger()
        logging.basicConfig(level=logging.DEBUG)
        global board
        global running
        global board_id
        global exg_channels
        global sampling_rate
        global save_resources
        board_id = BoardIds.SYNTHETIC_BOARD if port == 'Synthetic' else BoardIds.CYTON_BOARD
        params = BrainFlowInputParams()
        params.serial_port = port
        params.serial_number = ''
        params.mac_address = ''
        params.other_info = ''
        params.ip_address = ''
        params.file = ''
        params.ip_protocol = 0
        params.ip_port = 0
        params.timeout = 0
        params.master_board = BoardIds.NO_BOARD
        exg_channels = BoardShim.get_exg_channels(board_id)[:8]
        sampling_rate = BoardShim.get_sampling_rate(board_id)
        board = BoardShim(board_id, params)
        board.prepare_session()
        board.start_stream(3600 * 5 * 60)
        eel.state("Running")
        eel.log("Stream started!")
        running = True
        while running:
            if save_resources:
                eel.sleep(0.005)  # 5ms
            else:
                eel.sleep(0.03)  # 30ms
                data = board.get_current_board_data(1260)[exg_channels]
                data = np.array(data)
                data = preprocess(data, board_id, [*range(len(exg_channels))]).tolist()
                eel.stream(data)
        board.stop_stream()
        board.release_session()
        eel.state("Idle")
        eel.log("Stream stopped!")

    except Exception as inst:
        eel.state("Error")
        eel.error(": ".join((type(inst).__name__,) + inst.args))
        raise inst


def get_board_data():
    global board
    if board:
        return board.get_board_data()
    else:
        return []


def get_current_board_data(samples):
    global board
    if board:
        return board.get_current_board_data(samples)
    else:
        return []

def get_exg_channels():
    global exg_channels
    return exg_channels

def get_board_id():
    global board_id
    return board_id

def limit_channels(data):
    if data.size == 0:
        return data
    curves = [None] * 8
    for count, channel in enumerate(exg_channels):
        if count >= 8:
            continue
        curves[count] = data[channel].tolist()
    return curves


def preprocess(data, board_id, exg_channels):
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    if data.size == 0:
        return data
    for _count, channel in enumerate(exg_channels):
        channel_data = data[channel].to_numpy() if isinstance(data[channel], pd.Series) else data[channel]
        DataFilter.detrend(channel_data, DetrendOperations.CONSTANT.value)
        DataFilter.remove_environmental_noise(channel_data, sampling_rate, NoiseTypes.SIXTY.value);
        DataFilter.perform_bandpass(channel_data, sampling_rate, 5, 230, 4, FilterTypes.BUTTERWORTH.value, 1.0)
        DataFilter.perform_bandstop(channel_data, sampling_rate, 115, 135, 4, FilterTypes.BUTTERWORTH.value, 1.0)
        DataFilter.perform_rolling_filter(channel_data, 3, AggOperations.MEAN.value)
    if isinstance(data[channel], pd.Series):
      return data.drop(data.columns[0],axis=1).to_numpy()
    return data


def set_save_resources(flag):
    global save_resources
    save_resources = flag
