from backend.cyton_stream import get_board_data, get_exg_channels
import pandas as pd
import random as rd
import numpy as np
import string
import math
import eel

loop_count = 0
total_loops = 0

def stop_recording_stream():
    global loop_count
    global total_loops
    loop_count = total_loops


def record_stream(saveasrec, wpm, period, one_stream, include_silence, include_fallback, words):
    global loop_count
    global total_loops
    if not saveasrec:
        saveasrec = ''.join(rd.choice(string.ascii_uppercase)
                            for i in range(10))
    saveasrec = saveasrec + '_1S' if one_stream else saveasrec
    last_word = None
    loop_count = 0
    total_loops = math.floor(period * wpm/60)
    timeout = 60/wpm
    word_history = []
    exg_channels = get_exg_channels()
    words.append("$FALLBACK") if include_fallback else None
    words.append("$SILENCE") if include_silence else None
    get_board_data()
    eel.record_step("$PREPARE", -1, total_loops)
    eel.sleep(3)
    get_board_data()

    emg_data = []
    # Display random word
    while loop_count < total_loops:
        word = current_word(words, loop_count, total_loops) if one_stream else random_word(words, last_word)
        word_history.append(word)
        last_word = word
        eel.record_step(word, loop_count, total_loops)
        loop_count += 1
        eel.sleep(timeout)
        emg_data.append(get_board_data()[exg_channels])

    eel.record_step("$END", loop_count, total_loops)

    eel.log("Saving to file...")

    for i in range(len(emg_data)):
      emg_data[i] = pd.DataFrame(np.transpose(emg_data[i]), columns=['Channel_{}'.format(x) for x in range(1, len(emg_data[i])+1)])
      emg_data[i].insert(loc=0, column='WORD', value=word_history[i])

    df = pd.concat(emg_data)

    # Write to file
    df.to_csv("dist/saves/%s.csv" % (saveasrec), index=False)
    eel.log("Saved as %s.csv" % (saveasrec))
    eel.sync_files()


def current_word(words, loop_count, total_loops):
    word_index = int(loop_count / total_loops * len(words))
    return words[word_index]

def random_word(words, last_word):
    word = rd.choice(words)
    return random_word(words, last_word) if word == last_word else word


def fix_width(new_col, shape, last_word):
    if new_col.shape[0] > shape:
        return np.delete(new_col, shape-new_col.shape[0])
    elif new_col.shape[0] < shape:
        return np.append(new_col, np.repeat(last_word, shape-new_col.shape[0]))
    else:
        return new_col
