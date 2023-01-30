import eel
import random as rd


def record_stream(wps, period, include_silence, include_fallback, words):
    last_word = None
    loop_count = 0
    total_loops = period * 60 * wps
    timeout = 1/wps
    words.append("$FALLBACK") if include_fallback else None
    words.append("$SILENCE") if include_silence else None
    eel.train_step("$PREPARE", loop_count, total_loops)
    eel.sleep(3)

    while loop_count < total_loops:
        loop_count += 1
        word = random_word(words, last_word)
        last_word = word
        print("%d/%d - %s" % (loop_count, total_loops, word))
        eel.train_step(word, loop_count, total_loops)
        eel.sleep(timeout)

def random_word(words, last_word):
    word = rd.choice(words)
    return random_word(words, last_word) if word == last_word else word
