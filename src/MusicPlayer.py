from pygame import mixer
import time

class MusicPlayer:
    def __init__(self):
        mixer.init()
        self.maxvolume = 0.75
        self.volume = self.maxvolume
        self.volumefadespeed = 0.02

    @property
    def isPlaying(self):
        return mixer.music.get_busy()

    def setVolume(self, volume):
        self.volume = volume
        mixer.music.set_volume(volume)

    def playSong(self, song):
        mixer.music.load(song)
        self.setVolume(self.maxvolume)
        mixer.music.play()

    def stopMusicIfPlaying(self):
        if mixer.music.get_busy():
            mixer.music.stop();

    def stop(self):
        if mixer.music.get_busy():
            mixer.music.stop()

    def pause(self):
        mixer.music.pause()

    def unpause(self):
        mixer.music.unpause()

    def fadeDownMusic(self, restart):
        while self.volume > 0:
            self.volume = self.volume - self.volumefadespeed
            if self.volume < 0:
                self.volume = 0

            self.setVolume(self.volume)
            time.sleep(0.05)

        if restart:
            self.stop()
        else:
            self.pause()

    def fadeUpMusic(self, restart):
        if not restart:
            self.unpause()
            while self.volume < self.maxvolume:
                self.volume = self.volume + self.volumefadespeed;
                if self.volume > self.maxvolume:
                    self.volume = self.maxvolume

                self.setVolume(self.volume)
                time.sleep(0.05)