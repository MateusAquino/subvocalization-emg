from pyOpenBCI import OpenBCICyton
from pylsl import StreamInfo, StreamOutlet, ContinuousResolver
import numpy as np
import random
import time

SCALE_FACTOR_EEG = ((4500000)/24/(2**23-1))/1.5  # uV/count


def stream():
    print("Creating LSL stream for EEG. \nName: OpenBCIEEG\nID: OpenBCItestEEG\n")
    info_eeg = StreamInfo('OpenBCIEEG', 'EEG', 8, 250,
                          'float32', 'OpenBCItestEEG')
    info = StreamInfo('MyMarkerStream', 'Markers',
                      6, 0, 'string', 'myuidw43536')
    outlet_eeg = StreamOutlet(info_eeg)
    outlet = StreamOutlet(info)
    marker_names = ['Marker']

    def lsl_streamers(sample):
        outlet_eeg.push_sample(np.array(sample.channels_data)*SCALE_FACTOR_EEG)
        outlet.push_sample(marker_names[0])
        print(np.array(sample.channels_data)*SCALE_FACTOR_EEG)

    board = OpenBCICyton(daisy=False)
    board.start_stream(lsl_streamers)
