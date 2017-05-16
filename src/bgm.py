import os
import random
import time
from Queue import LifoQueue
from ConfigParser import SafeConfigParser

from MusicPlayer import MusicPlayer
from ProcessService import ProcessService


class State:
    def __init__(self, musicPlayer):
        self.musicPlayer = musicPlayer


class FadeUpState(State):
    def run(self):
        self.musicPlayer.fadeUpMusic()

    def nextState(self, status):
        return State.playingMusic


class FadeDownState(State):
    def __init__(self, musicPlayer, restart):
        State.__init__(self, musicPlayer)
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

class Application:
    random.seed()

    def __init__(self, process_service, music_player, settings):
        self.processService = process_service
        self.musicPlayer = music_player

        self.startdelay = settings.getint("default", "startdelay")
        self.musicdir = settings.get("default", "musicdir")
        self.restart = settings.getboolean("default", "restart")
        self.startsong = settings.get("default", "startsong")

        self.emulatornames = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi", "linapple", "hatari", "stella",
                              "atari800", "xroar", "vice", "daphne", "reicast", "pifba", "osmose", "gpsp", "jzintv",
                              "basiliskll", "mame", "advmame", "dgen", "openmsx", "mupen64plus", "gngeo", "dosbox",
                              "ppsspp", "simcoupe", "scummvm", "snes9x", "pisnes", "frotz", "fbzx", "fuse", "gemrb",
                              "cgenesis", "zdoom", "eduke32", "lincity", "love", "kodi", "alephone", "micropolis",
                              "openbor", "openttd", "opentyrian", "cannonball", "tyrquake", "ioquake3", "residualvm",
                              "xrick", "sdlpop", "uqm", "stratagus", "wolf4sdl", "solarus"]

        State.paused = Paused(music_player)
        State.stopMusic = StopMusic(music_player)
        State.stopped = Stopped(music_player)
        State.playingMusic = PlayingMusic(music_player)
        State.fadeUp = FadeUpState(music_player)
        State.fadeDown = FadeDownState(music_player, self.restart)
        State.playMusic = PlayMusic(music_player, self.startsong, self.musicdir)

        if self.musicPlayer.isPlaying:
            self.currentState = State.playingMusic
        elif self.musicPlayer.isPaused:
            self.currentState = State.paused
        else:
            self.currentState = State.stopped



    def getState(self):

        state = {
            "musicIsDisabled": self.musicIsDisabled(),
            "esRunning": self.processService.processIsRunning("emulationstatio"),
            "emulatorIsRunning": self.processService.anyProcessIsRunning(self.emulatornames),
            "songIsBeingPlayed": self.musicPlayer.isPlaying,
            "restart": self.restart
        }

        return state

    def waitForProcess(self, process_name):
        while not self.processService.processIsRunning(process_name):
            time.sleep(1)

    def musicIsDisabled(self):
        return os.path.exists('/home/pi/PyScripts/DisableMusic')

    def waitomxPlayer(self):
        # Look for OMXplayer - if it's running, someone's got a splash screen going!

        while self.processService.processIsRunning("omxplayer"):
            time.sleep(1)  # OMXPlayer is running, sleep 1 to prevent the need for a splash.

        while self.processService.processIsRunning("omxplayer.bin"):
            time.sleep(1)

    def executeState(self):

        self.currentState = self.currentState.nextState(self.getState())
        self.currentState.run()

    def run(self):

        # Delay audio start per config option above
        if self.startdelay > 0:
            time.sleep(self.startdelay)

        self.waitomxPlayer()

        while True:
            self.executeState()


if __name__ == '__main__':
    config = SafeConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
    Application(ProcessService(), MusicPlayer(), config).run()
