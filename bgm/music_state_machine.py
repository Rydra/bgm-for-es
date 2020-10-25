import random
import os
import time
from enum import Enum, auto
from queue import LifoQueue


class MusicState(Enum):
    PAUSED = auto()
    STOPPED = auto()
    PLAYING_MUSIC = auto()


class MusicStateMachine:
    random.seed()

    class _EnvironmentStatus:
        def __init__(self, music_is_disabled, es_running, emulator_is_running, song_is_being_played, restart):
            self.restart = restart
            self.song_is_being_played = song_is_being_played
            self.emulator_is_running = emulator_is_running
            self.es_running = es_running
            self.music_is_disabled = music_is_disabled

    def __init__(self,
                 process_service,
                 music_player,
                 settings,
                 forced_initial_status=None,
                 forced_es_process=None,
                 forced_emulators=None):

        self._process_service = process_service
        self._music_player = music_player

        self._startdelay = settings.getint("default", "startdelay")
        self._musicdir = settings.get("default", "musicdir")
        self._restart = settings.getboolean("default", "restart")
        self._startsong = settings.get("default", "startsong")

        self._song_queue = self._generate_random_music_queue()

        self._emulationstation_procname = forced_es_process or "emulationstatio"
        self._emulator_names = forced_emulators or ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi", "linapple", "hatari", "stella",
                              "atari800", "xroar", "vice", "daphne", "reicast", "pifba", "osmose", "gpsp", "jzintv",
                              "basiliskll", "mame", "advmame", "dgen", "openmsx", "mupen64plus", "gngeo", "dosbox",
                              "ppsspp", "simcoupe", "scummvm", "snes9x", "pisnes", "frotz", "fbzx", "fuse", "gemrb",
                              "cgenesis", "zdoom", "eduke32", "lincity", "love", "kodi", "alephone", "micropolis",
                                                    "openbor", "openttd", "opentyrian", "cannonball", "tyrquake", "ioquake3", "residualvm",
                                                    "xrick", "sdlpop", "uqm", "stratagus", "wolf4sdl", "solarus"]

        self._transitionTable = {
            MusicState.PAUSED: [
                (self.has_to_stop_music, self.stop_music, MusicState.STOPPED),
                (self.emulator_is_not_running, self.fade_up, MusicState.PLAYING_MUSIC),
                (None, self.delay, MusicState.PAUSED)],

            MusicState.STOPPED: [
                (self.has_to_play_music, self.play_music, MusicState.PLAYING_MUSIC),
                (None, self.delay, MusicState.STOPPED)],

            MusicState.PLAYING_MUSIC: [
                (self.has_to_stop_music, self.stop_music, MusicState.STOPPED),
                (self.should_fade_down_and_pause, self.fade_down, MusicState.PAUSED),
                (self.should_fade_down_and_stop, self.fade_down, MusicState.STOPPED),
                (self._music_is_not_playing, self.play_music, MusicState.PLAYING_MUSIC),
                (None, self.delay, MusicState.PLAYING_MUSIC)]
        }

        self._currentState = forced_initial_status or self._get_initial_state()

    def execute_state(self):

        status = self._get_status()
        transitions = self._transitionTable[self._currentState]
        for condition, action, nextState in transitions:

            if condition is None or condition(status):
                action()
                self._currentState = nextState
                break

    def run(self):
        if self._startdelay > 0:
            time.sleep(self._startdelay)

        self._wait_omxplayer()

        while True:
            self.execute_state()

    def _get_songs(self):
        return [song for song in os.listdir(self._musicdir) if song[-4:] == ".mp3" or song[-4:] == ".ogg"]

    def _generate_random_music_queue(self):
        song_queue = LifoQueue()
        song_list = self._get_songs()

        if self._startsong in song_list:
            song_queue.put(self._startsong)
            song_list.remove(self._startsong)

        while len(song_list) > 0:
            song_to_add = random.randint(0, len(song_list) - 1)
            song_queue.put(song_list[song_to_add])
            song_list.remove(song_list[song_to_add])

        return song_queue

    # ACTIONS

    def delay(self):
        time.sleep(2)

    def stop_music(self):
        self._music_player.stop()

    def fade_up(self):
        self._music_player.fade_up_music()

    def fade_down(self):
        self._music_player.fade_down_music(not self._restart)

    def play_music(self):
        if self._song_queue.empty():
            self._song_queue = self._generate_random_music_queue()

        song = os.path.join(self._musicdir, self._song_queue.get())
        self._music_player.play_song(song)

    # CONDITIONS

    def has_to_stop_music(self, status):
        return not status.emulator_is_running and (status.music_is_disabled or not status.es_running)

    def emulator_is_not_running(self, status):
        return not status.emulator_is_running

    def should_fade_down_and_stop(self, status):
        return status.emulator_is_running and self._restart

    def should_fade_down_and_pause(self, status):
        return status.emulator_is_running and not self._restart

    def has_to_play_music(self, status):
        return status.es_running and not status.emulator_is_running

    def _music_is_not_playing(self, status):
        return not self._music_player.is_playing

    def _get_initial_state(self):
        if self._music_player.is_playing:
            return MusicState.PLAYING_MUSIC
        elif self._music_player.is_paused:
            return MusicState.PAUSED
        else:
            return MusicState.STOPPED

    def _get_status(self):

        status = self._EnvironmentStatus(
            emulator_is_running=self._process_service.any_process_is_running(self._emulator_names),
            es_running=self._process_service.process_is_running(self._emulationstation_procname),
            music_is_disabled=self._music_is_disabled(),
            restart=self._restart,
            song_is_being_played=self._music_player.is_playing
        )

        return status

    def _wait_for_process(self, process_name):
        while not self._process_service.process_is_running(process_name):
            time.sleep(1)

    def _music_is_disabled(self):
        return os.path.exists('/home/pi/PyScripts/DisableMusic')

    def _wait_omxplayer(self):
        # Look for OMXplayer - if it's running, someone's got a splash screen going!

        while self._process_service.process_is_running("omxplayer"):
            time.sleep(1)  # OMXPlayer is running, sleep 1 to prevent the need for a splash.

        while self._process_service.process_is_running("omxplayer.bin"):
            time.sleep(1)
