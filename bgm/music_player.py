from pygame import mixer
import time


class MusicPlayer:
    def __init__(self):
        mixer.init()
        self._is_paused = False
        self._maxvolume = 0.75
        self._volume = self._maxvolume
        self._volume_fadespeed = 0.02

    @property
    def is_playing(self):
        return mixer.music.get_busy()

    @property
    def is_paused(self):
        return self._is_paused

    def play_song(self, song):
        mixer.music.load(song)
        self._is_paused = False
        self._set_volume(self._maxvolume)
        mixer.music.play()

    def stop_music_if_playing(self):
        if mixer.music.get_busy():
            self._is_paused = False
            mixer.music.stop()

    def stop(self):
        self._is_paused = False
        if mixer.music.get_busy():
            mixer.music.stop()

    def fade_down_music(self, pause):
        """
        Fades down the current song until stopped. If pause is True,
        it will resume the current song when starting again
        """
        while self._volume > 0:
            self._volume = self._volume - self._volume_fadespeed
            if self._volume < 0:
                self._volume = 0

            self._set_volume(self._volume)
            time.sleep(0.05)

        if pause:
            self._pause()
        else:
            self.stop()

    def fade_up_music(self):
        self._unpause()
        while self._volume < self._maxvolume:
            self._volume = self._volume + self._volume_fadespeed
            if self._volume > self._maxvolume:
                self._volume = self._maxvolume

            self._set_volume(self._volume)
            time.sleep(0.05)

    def _pause(self):
        self._is_paused = True
        mixer.music.pause()

    def _unpause(self):
        self._is_paused = False
        mixer.music.unpause()

    def _set_volume(self, volume):
        self._volume = volume
        mixer.music.set_volume(volume)
