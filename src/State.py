import time
import os
import random

from Queue import LifoQueue


class State:
    def __init__(self, music_player):
        self.musicPlayer = music_player

    def run(self):
        pass

    def nextState(self, status):
        pass


class FadeUpState(State):
    def run(self):
        self.musicPlayer.fadeUpMusic()

    def nextState(self, status):
        return State.playingMusic


class FadeDownState(State):
    def __init__(self, music_player, restart):
        State.__init__(self, music_player)
        self.restart = restart

    def run(self):
        self.musicPlayer.fadeDownMusic(not self.restart)

    def nextState(self, status):
        if self.restart:
            return State.stopped
        return State.paused


class Paused(State):
    def run(self):
        time.sleep(2)

    def nextState(self, status):
        if not status["emulatorIsRunning"]:
            if status["musicIsDisabled"] or not status["esRunning"]:
                return State.stopMusic
            else:
                return State.fadeUp

        return State.paused


class PlayingMusic(State):
    def run(self):
        time.sleep(2)

    def nextState(self, status):
        if status["musicIsDisabled"] or not status["esRunning"]:
            return State.stopMusic
        if status["emulatorIsRunning"]:
            return State.fadeDown
        if not self.musicPlayer.isPlaying:
            return State.playMusic

        return State.playingMusic


class PlayMusic(State):
    def __init__(self, musicPlayer, start_song, musicdir):
        State.__init__(self, musicPlayer)
        self.startsong = start_song
        self.musicdir = musicdir
        self.songQueue = self.getRandomQueue()

    def getSongs(self):
        return [song for song in os.listdir(self.musicdir) if song[-4:] == ".mp3" or song[-4:] == ".ogg"]

    def getRandomQueue(self):

        song_queue = LifoQueue()
        song_list = self.getSongs()

        if self.startsong in song_list:
            song_queue.put(self.startsong)
            song_list.remove(self.startsong)

        while len(song_list) > 0:
            song_to_add = random.randint(0, len(song_list) - 1)
            song_queue.put(song_list[song_to_add])
            song_list.remove(song_list[song_to_add])

        return song_queue

    def run(self):
        if self.songQueue.empty():
            self.songQueue = self.getRandomQueue()

        song = os.path.join(self.musicdir, self.songQueue.get())
        self.musicPlayer.playSong(song)

    def nextState(self, status):
        return State.playingMusic


class Stopped(State):
    def run(self):
        time.sleep(2)

    def nextState(self, status):
        if status["esRunning"] and not status["emulatorIsRunning"]:
            return State.playMusic

        return State.stopped


class StopMusic(State):
    def run(self):
        self.musicPlayer.stop()

    def nextState(self, status):
        return State.stopped
