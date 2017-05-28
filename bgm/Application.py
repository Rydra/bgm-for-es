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

    def get_songs(self):
        return [song for song in os.listdir(self.musicdir) if song[-4:] == ".mp3" or song[-4:] == ".ogg"]

    def get_random_queue(self):

        song_queue = LifoQueue()
        song_list = self.get_songs()

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

    def stop_music(self):
        self.musicPlayer.stop()

    def fade_up(self):
        self.musicPlayer.fade_up_music()

    def fade_down(self):
        self.musicPlayer.fade_down_music(not self.restart)

    def play_music(self):
        if self.songQueue.empty():
            self.songQueue = self.get_random_queue()

        song = os.path.join(self.musicdir, self.songQueue.get())
        self.musicPlayer.play_song(song)

    # CONDITIONS

    def has_to_stop_music(self, status):
        return not status["emulatorIsRunning"] and (status["musicIsDisabled"] or not status["esRunning"])

    def emulator_is_not_running(self, status):
        return not status["emulatorIsRunning"]

    def should_fade_down_and_stop(self, status):
        return status["emulatorIsRunning"] and self.restart

    def should_fade_down_and_pause(self, status):
        return status["emulatorIsRunning"] and not self.restart

    def has_to_play_music(self, status):
        return status["esRunning"] and not status["emulatorIsRunning"]

    def music_is_not_playing(self, status):
        return not self.musicPlayer.isPlaying

    def __init__(self, process_service, music_player, settings, forced_initial_status = None):
        self.processService = process_service
        self.musicPlayer = music_player

        self.startdelay = settings.getint("default", "startdelay")
        self.musicdir = settings.get("default", "musicdir")
        self.restart = settings.getboolean("default", "restart")
        self.startsong = settings.get("default", "startsong")

        self.songQueue = self.get_random_queue()

        self.emulatornames = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi", "linapple", "hatari", "stella",
                              "atari800", "xroar", "vice", "daphne", "reicast", "pifba", "osmose", "gpsp", "jzintv",
                              "basiliskll", "mame", "advmame", "dgen", "openmsx", "mupen64plus", "gngeo", "dosbox",
                              "ppsspp", "simcoupe", "scummvm", "snes9x", "pisnes", "frotz", "fbzx", "fuse", "gemrb",
                              "cgenesis", "zdoom", "eduke32", "lincity", "love", "kodi", "alephone", "micropolis",
                              "openbor", "openttd", "opentyrian", "cannonball", "tyrquake", "ioquake3", "residualvm",
                              "xrick", "sdlpop", "uqm", "stratagus", "wolf4sdl", "solarus"]

        self.transitionTable = {
            State.paused: [
                (self.has_to_stop_music, self.stop_music, State.stopped),
                (self.emulator_is_not_running, self.fade_up, State.playingMusic),
                (None, self.delay, State.paused)],

            State.stopped: [
                (self.has_to_play_music, self.play_music, State.playingMusic),
                (None, self.delay, State.stopped)],

            State.playingMusic: [
                (self.has_to_stop_music, self.stop_music, State.stopped),
                (self.should_fade_down_and_pause, self.fade_down, State.paused),
                (self.should_fade_down_and_stop, self.fade_down, State.stopped),
                (self.music_is_not_playing, self.play_music, State.playingMusic),
                (None, self.delay, State.playingMusic)]
        }

        if forced_initial_status is None:
            self.currentState = self.get_initial_state()
        else:
            self.currentState = forced_initial_status

    def get_initial_state(self):
        if self.musicPlayer.isPlaying:
            return State.playingMusic
        elif self.musicPlayer.isPaused:
            return State.paused
        else:
            return State.stopped

    def get_state(self):

        state = {
            "musicIsDisabled": self.music_is_disabled(),
            "esRunning": self.processService.process_is_running("emulationstatio"),
            "emulatorIsRunning": self.processService.any_process_is_running(self.emulatornames),
            "songIsBeingPlayed": self.musicPlayer.isPlaying,
            "restart": self.restart
        }

        return state

    def wait_for_process(self, process_name):
        while not self.processService.process_is_running(process_name):
            time.sleep(1)

    def music_is_disabled(self):
        return os.path.exists('/home/pi/PyScripts/DisableMusic')

    def wait_omxplayer(self):
        # Look for OMXplayer - if it's running, someone's got a splash screen going!

        while self.processService.process_is_running("omxplayer"):
            time.sleep(1)  # OMXPlayer is running, sleep 1 to prevent the need for a splash.

        while self.processService.process_is_running("omxplayer.bin"):
            time.sleep(1)

    def execute_state(self):

        status = self.get_state()
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

        self.wait_omxplayer()

        while True:
            self.execute_state()
