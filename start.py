import eel
import backend.bridge

try:
    eel.start('index.html', mode='None')
except (SystemExit, MemoryError, KeyboardInterrupt):
    pass
