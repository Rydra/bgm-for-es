from pygame import mixer
import time

class MusicPlayer:
    def __init__(self):
        mixer.init()
        self.isPaused = False
        self.maxvolume = 0.75
        self.volume = self.maxvolume
        self.volumefadespeed = 0.02

    @property
    def isPlaying(self):
        return mixer.music.get_busy()

    @property
    def isPaused(self):
        return self.isPaused

    def setVolume(self, volume):
        self.volume = volume
        mixer.music.set_volume(volume)

    def playSong(self, song):
        mixer.music.load(song)
        self.isPaused = False
        self.setVolume(self.maxvolume)
        mixer.music.play()

    def stopMusicIfPlaying(self):
        if mixer.music.get_busy():
            self.isPaused = False
            mixer.music.stop()

    def stop(self):
        self.isPaused = False
        if mixer.music.get_busy():
            mixer.music.stop()

    def pause(self):
        self.isPaused = True
        mixer.music.pause()

    def unpause(self):
        self.isPaused = False
        mixer.music.unpause()

    def fadeDownMusic(self, pause):
        while self.volume > 0:
            self.volume = self.volume - self.volumefadespeed
            if self.volume < 0:
                self.volume = 0

            self.setVolume(self.volume)
            time.sleep(0.05)

        if pause:
            self.pause()
        else:
            self.stop()

    def fadeUpMusic(self):
        self.unpause()
        while self.volume < self.maxvolume:
            self.volume = self.volume + self.volumefadespeed;
            if self.volume > self.maxvolume:
                self.volume = self.maxvolume

            self.setVolume(self.volume)
            time.sleep(0.05)