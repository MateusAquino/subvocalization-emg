import os
import vlc
import gtts
import random
import string

def play(filename):
    vlc.MediaPlayer(filename).play()

def speak(text):
    if text == " ": return
    tts = gtts.gTTS(text=text, lang="pt")
    hash = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    filename = "dist/tts-" + hash + ".mp3"
    tts.save(filename)
    player = vlc.MediaPlayer(filename)
    callback = lambda _event: os.remove(filename)
    events = player.event_manager()
    events.event_attach(vlc.EventType.MediaPlayerEndReached, callback)
    player.play()
