from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import argparse
import logging
import eel

running = False
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
        parser = argparse.ArgumentParser()

        if port == 'Synthetic':
            board_id = BoardIds.SYNTHETIC_BOARD
        else:
            board_id = BoardIds.CYTON_BOARD

        parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                            default=0)
        parser.add_argument('--ip-port', type=int,
                            help='ip port', required=False, default=0)
        parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                            default=0)
        parser.add_argument('--ip-address', type=str,
                            help='ip address', required=False, default='')
        parser.add_argument('--serial-port', type=str,
                            help='serial port', required=False, default=port)
        parser.add_argument('--mac-address', type=str,
                            help='mac address', required=False, default='')
        parser.add_argument('--other-info', type=str,
                            help='other info', required=False, default='')
        parser.add_argument('--serial-number', type=str,
                            help='serial number', required=False, default='')
        parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                            required=False, default=board_id)
        parser.add_argument('--file', type=str, help='file',
                            required=False, default='')
        parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                            required=False, default=BoardIds.NO_BOARD)
        args = parser.parse_args()

        params = BrainFlowInputParams()
        params.ip_port = args.ip_port
        params.serial_port = args.serial_port
        params.mac_address = args.mac_address
        params.other_info = args.other_info
        params.serial_number = args.serial_number
        params.ip_address = args.ip_address
        params.ip_protocol = args.ip_protocol
        params.timeout = args.timeout
        params.file = args.file
        params.master_board = args.master_board

        global board
        global running
        global exg_channels
        global sampling_rate
        exg_channels = BoardShim.get_exg_channels(args.board_id)
        sampling_rate = BoardShim.get_sampling_rate(args.board_id)
        board = BoardShim(args.board_id, params)
        board.prepare_session()
        board.start_stream(3600 * 5 * 60)
        eel.state("Running")
        eel.log("Stream started!")
        running = True
        while running:
            eel.sleep(0.05)  # 50ms
            data = board.get_current_board_data(sampling_rate*10)
            preprocessed_data = preprocess(data)
            eel.stream(preprocessed_data)
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

def limit_channels(data):
    if data.size == 0:
        return data
    curves = [None] * 8
    for count, channel in enumerate(exg_channels):
        if count >= 8:
            continue
        curves[count] = data[channel].tolist()
    return curves

def preprocess(data):
    if data.size == 0:
        return data
    curves = [None] * 8
    for count, channel in enumerate(exg_channels):
        if count >= 8:
            continue
        DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
        DataFilter.perform_bandpass(data[channel], sampling_rate, 3.0, 45.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        DataFilter.perform_bandstop(data[channel], sampling_rate, 48.0, 52.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        DataFilter.perform_bandstop(data[channel], sampling_rate, 58.0, 62.0, 2,
                                    FilterTypes.BUTTERWORTH.value, 0)
        curves[count] = data[channel].tolist()
    return curves
