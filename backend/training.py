import eel
import random as rd


def train_stream(wps, period, include_silence, include_fallback, words):
    loop_count = 0
    total_loops = period * 60 * wps
    timeout = 1/wps

    while loop_count < total_loops:
        loop_count += 1
        print("%d/%d" % (loop_count, total_loops))
        eel.sleep(timeout)


def random_word(words, include_silence, include_fallback):
  # if include_fallback or include_silence:
    # if rd.random < .90:
    rd.choice(words)
    # else:
    # if include_silence
