import random
import os
from Queue import LifoQueue
import time


class State:
    def __init__(self, name):
        self.name = name

State.paused = State("Paused")
State.stopped = State("Stopped")
State.playingMusic = State("PlayingMusic")


class Application:
    random.seed()

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

    # ACTIONS

    def delay(self):
        time.sleep(2)

    def stopMusic(self):
        self.musicPlayer.stop()

    def fadeUp(self):
        self.musicPlayer.fadeUpMusic()

    def fadeDown(self):
        self.musicPlayer.fadeDownMusic(not self.restart)

    def playMusic(self):
        if self.songQueue.empty():
            self.songQueue = self.getRandomQueue()

        song = os.path.join(self.musicdir, self.songQueue.get())
        self.musicPlayer.playSong(song)

    # CONDITIONS

    def hasToStopMusic(self, status):
        return not status["emulatorIsRunning"] and (status["musicIsDisabled"] or not status["esRunning"])

    def emulatorIsNotRunning(self, status):
        return not status["emulatorIsRunning"]

    def shouldFadeDownAndStop(self, status):
        return status["emulatorIsRunning"] and self.restart

    def shouldFadeDownAndPause(self, status):
        return status["emulatorIsRunning"] and not self.restart

    def hasToPlayMusic(self, status):
        return status["esRunning"] and not status["emulatorIsRunning"]

    def musicIsNotPlaying(self, status):
        return not self.musicPlayer.isPlaying

    def __init__(self, process_service, music_player, settings, forced_initial_status = None):
        self.processService = process_service
        self.musicPlayer = music_player

        self.startdelay = settings.getint("default", "startdelay")
        self.musicdir = settings.get("default", "musicdir")
        self.restart = settings.getboolean("default", "restart")
        self.startsong = settings.get("default", "startsong")

        self.songQueue = self.getRandomQueue()

        self.emulatornames = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi", "linapple", "hatari", "stella",
                              "atari800", "xroar", "vice", "daphne", "reicast", "pifba", "osmose", "gpsp", "jzintv",
                              "basiliskll", "mame", "advmame", "dgen", "openmsx", "mupen64plus", "gngeo", "dosbox",
                              "ppsspp", "simcoupe", "scummvm", "snes9x", "pisnes", "frotz", "fbzx", "fuse", "gemrb",
                              "cgenesis", "zdoom", "eduke32", "lincity", "love", "kodi", "alephone", "micropolis",
                              "openbor", "openttd", "opentyrian", "cannonball", "tyrquake", "ioquake3", "residualvm",
                              "xrick", "sdlpop", "uqm", "stratagus", "wolf4sdl", "solarus"]

        self.transitionTable = {
            State.paused: [
                (self.hasToStopMusic, self.stopMusic, State.stopped),
                (self.emulatorIsNotRunning, self.fadeUp, State.playingMusic),
                (None, self.delay, State.paused)],

            State.stopped: [
                (self.hasToPlayMusic, self.playMusic, State.playingMusic),
                (None, self.delay, State.stopped)],

            State.playingMusic: [
                (self.hasToStopMusic, self.stopMusic, State.stopped),
                (self.shouldFadeDownAndPause, self.fadeDown, State.paused),
                (self.shouldFadeDownAndStop, self.fadeDown, State.stopped),
                (self.musicIsNotPlaying, self.playMusic, State.playingMusic),
                (None, self.delay, State.playingMusic)]
        }

        if forced_initial_status is None:
            self.currentState = self.getInitialState()
        else:
            self.currentState = forced_initial_status

    def getInitialState(self):
        if self.musicPlayer.isPlaying:
            return State.playingMusic
        elif self.musicPlayer.isPaused:
            return State.paused
        else:
            return State.stopped

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

        status = self.getState()
        transitions = self.transitionTable[self.currentState]
        for condition, action, nextState in transitions:

            if condition is None or condition(status):
                action()
                self.currentState = nextState
                break

    def run(self):

        # Delay audio start per config option above
        if self.startdelay > 0:
            time.sleep(self.startdelay)

        self.waitomxPlayer()

        while True:
            self.executeState()
