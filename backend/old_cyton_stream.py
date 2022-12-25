from pyOpenBCI import OpenBCICyton
from pylsl import StreamInfo, StreamOutlet
import numpy as np
import eel

SCALE_FACTOR_EEG = (4500000)/24/(2**23-1)
board = None


def stop_stream():
    if board != None:
        board.stop_stream()


def start_stream():
    try:
        eel.state("Starting")
        eel.log("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")
        info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250,
                              'float32', 'OpenBCItestEEG')
        info = StreamInfo('MyMarkerStream', 'Markers',
                          6, 0, 'string', 'myuidw43536')
        outlet_eeg = StreamOutlet(info_eeg)
        outlet = StreamOutlet(info)
        marker_names = ['Marker']

        def lsl_streamers(sample):
            data = np.array(sample.channels_data)*SCALE_FACTOR_EEG
            outlet_eeg.push_sample(data)
            outlet.push_sample(marker_names[0])
            eel.stream(str(data))
            eel.sleep(0.00000000000001)

        global board
        board = OpenBCICyton(daisy=False)
        eel.state("Running")
        eel.log("Stream started!")
        board.start_stream(lsl_streamers)
        eel.state("Idle")
        eel.log("Stream stopped!")

    except Exception as inst:
        eel.state("Error")
        eel.error(": ".join((type(inst).__name__,) + inst.args))
        raise inst
