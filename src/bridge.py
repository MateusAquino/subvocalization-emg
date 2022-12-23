from src.cyton_stream import stream
import eel


@eel.expose
def start_session():
    try:
        stream()
    except Exception as inst:
        eel.error(": ".join((type(inst).__name__,) + inst.args))
        raise inst


eel.init('gui')
