from backend.cyton_stream import get_board_data, limit_channels, set_save_resources
from brainflow.data_filter import DataFilter
import pandas as pd
import random as rd
import numpy as np
import string
import eel


def record_stream(saveasrec, wps, period, include_silence, include_fallback, words):
    if not saveasrec:
        saveasrec = ''.join(rd.choice(string.ascii_uppercase)
                            for i in range(10))
    last_word = None
    loop_count = 0
    total_loops = period * wps
    timeout = 1/wps
    word_history = []
    words.append("$FALLBACK") if include_fallback else None
    words.append("$SILENCE") if include_silence else None
    eel.record_step("$PREPARE", -1, total_loops)
    set_save_resources(True)
    eel.sleep(3)
    get_board_data()

    # Display random word
    while loop_count < total_loops:
        word = random_word(words, last_word)
        word_history.append(word)
        last_word = word
        eel.record_step(word, loop_count, total_loops)
        loop_count += 1
        print("%d/%d - %s" % (loop_count, total_loops, word))
        eel.sleep(timeout)

    data = get_board_data()
    set_save_resources(False)
    eel.record_step("$END", loop_count, total_loops)
    transposed_data = np.transpose(limit_channels(data))
    word_history = np.transpose(word_history)

    eel.log("Saving to file...")
    df = pd.DataFrame(transposed_data, columns=['Channel_{}'.format(
        x) for x in range(1, transposed_data.shape[1]+1)])
    rows = transposed_data.shape[0]
    new_col = np.repeat(word_history, rows/word_history.shape[0])
    new_col = fix_width(new_col, rows, last_word)
    df.insert(loc=0, column='WORD', value=new_col)

    # Write to file
    df.to_csv("dist/saves/%s.csv" % (saveasrec), index=False)
    eel.log("Saved as %s.csv" % (saveasrec))
    eel.sync_files()


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
