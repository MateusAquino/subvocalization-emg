from backend.cyton_stream import is_session_running, start_stream, stop_stream, set_save_resources
from backend.recording import record_stream
from backend.training import train_data
from backend.classifier import predict_emg, stop_predicting_stream
from shutil import rmtree
from os import walk, remove
import glob
import eel
import sys


@eel.expose
def setup():
    eel.sync_files()
    update_ports()
    set_save_resources(False)
    if (is_session_running()):
        eel.state("Running")
    else:
        eel.state("Idle")


@eel.expose
def start_session(port):
    eel.spawn(start_stream, port)


@eel.expose
def stop_session():
    try:
        stop_stream()
    except Exception as inst:
        eel.state("Error")
        eel.error(": ".join((type(inst).__name__,) + inst.args))
        raise inst


@eel.expose
def update_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usbserial*')
    else:
        []
    eel.set_ports(ports)


@eel.expose
def start_recording(saveasrec, wps, period, silence, fallback, words):
    wps = int(wps)
    period = int(period)
    eel.spawn(record_stream, saveasrec, wps, period, silence, fallback, words)


@eel.expose
def list_saves():
    saves = next(walk("dist/saves"), (None, None, []))[2]
    if ".gitignore" in saves:
        saves.remove(".gitignore")
    return saves


@eel.expose
def list_networks():
    networks = next(walk("dist/networks"), (None, None, []))[1]
    return networks


@eel.expose
def delete_save(save):
    remove("dist/saves/%s.csv" % (save))
    eel.sync_files()


@eel.expose
def delete_network(network):
    rmtree("dist/networks/" + network)
    eel.sync_files()


@eel.expose
def start_training(file_name, ratio, recordings, batch_size, epochs):
    ratio = int(ratio)
    batch_size = int(batch_size)
    epochs = int(epochs)
    eel.spawn(train_data, file_name, ratio, recordings, batch_size, epochs)


@eel.expose
def start_predicting(network_id, history_count, refresh_rate):
    history_count = int(history_count)
    refresh_rate = int(refresh_rate) / 1000.0
    eel.spawn(predict_emg, network_id, history_count, refresh_rate)


@eel.expose
def stop_predicting():
    stop_predicting_stream()


eel.init('frontend')
