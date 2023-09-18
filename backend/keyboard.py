from pynput.keyboard import Key, Controller

def press(key):
    if key == " ": return
    kb = Controller()
    if key in Key.__members__:
        kb.press(Key[key])
        kb.release(Key[key])
    else:
        try:
          kb.press(key)
          kb.release(key)
        except:
          pass
