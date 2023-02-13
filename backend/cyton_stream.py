from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import argparse
import logging
import eel

running = False
save_resources = False
board = None
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
        exg_channels = BoardShim.get_exg_channels(board_id)
        sampling_rate = BoardShim.get_sampling_rate(board_id)
        board = BoardShim(board_id, params)
        board.prepare_session()
        board.start_stream(3600 * 5 * 60)
        eel.state("Running")
        eel.log("Stream started!")
        running = True
        while running:
            if save_resources:
                eel.sleep(0.001)  # 1ms
            else:
                eel.sleep(0.05)  # 50ms
                data = board.get_current_board_data(sampling_rate*10)
                data = limit_channels(data)
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
    curves = [None] * 8
    for count, channel in enumerate(exg_channels):
        if count >= 8:
            continue
        channel_data = data[channel].to_numpy() if isinstance(
            data[channel], pd.Series) else data[channel]
        DataFilter.detrend(channel_data, DetrendOperations.CONSTANT.value)
        DataFilter.perform_bandpass(channel_data, sampling_rate, 3.0, 45.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        DataFilter.perform_bandstop(channel_data, sampling_rate, 48.0, 52.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        DataFilter.perform_bandstop(channel_data, sampling_rate, 58.0, 62.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        curves[count] = channel_data.tolist()
    return curves


def set_save_resources(flag):
    global save_resources
    save_resources = flag
