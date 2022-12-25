from backend.cyton_stream import *
import eel
import sys
import glob


@eel.expose
def setup():
    update_ports()
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


eel.init('frontend')
