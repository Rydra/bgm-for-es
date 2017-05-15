import os
import random
import time
from Queue import LifoQueue
from ConfigParser import SafeConfigParser

from MusicPlayer import MusicPlayer
from ProcessService import ProcessService


class Application:
    random.seed()

    def __init__(self, process_service, music_player, settings):
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

    def getState(self):

        state = {
            "musicIsDisabled": self.musicIsDisabled(),
            "esRunning": self.processService.processIsRunning("emulationstatio"),
            "emulatorIsRunning": self.processService.anyProcessIsRunning(self.emulatornames),
            "songIsBeingPlayed": self.musicPlayer.isPlaying
        }

        return state

    def waitForProcess(self, process_name):
        while not self.processService.processIsRunning(process_name):
            time.sleep(1)

    def musicIsDisabled(self):
        return os.path.exists('/home/pi/PyScripts/DisableMusic')

    def waitomxPlayer(self):
        # Look for OMXplayer - if it's running, someone's got a splash screen going!

        omxplayer_pid = self.processService.findPid("omxplayer")
        if omxplayer_pid != -1:
            while os.path.exists('/proc/' + omxplayer_pid):
                time.sleep(1)  # OMXPlayer is running, sleep 1 to prevent the need for a splash.

        omxplayer_pid = self.processService.findPid("omxplayer.bin")
        if omxplayer_pid != -1:
            while os.path.exists('/proc/' + omxplayer_pid):
                time.sleep(1)

    def executeState(self):
        new_state = self.getState()

        if self.musicPlayer.isPaused and not new_state["emulatorIsRunning"]:
            print("Fading up")
            self.musicPlayer.fadeUpMusic()

        elif new_state["musicIsDisabled"] or (not new_state["esRunning"] and not new_state["emulatorIsRunning"]):
            print("Music disabled! Stop")
            self.musicPlayer.stop()
            time.sleep(2)

        elif new_state["esRunning"] and not new_state["emulatorIsRunning"] and not self.musicPlayer.isPlaying:
            if self.songQueue.empty():
                self.songQueue = self.getRandomQueue()

            song = os.path.join(self.musicdir, self.songQueue.get())
            self.musicPlayer.playSong(song)

            print("BGM Now Playing: " + song)
            time.sleep(2)

        elif new_state["songIsBeingPlayed"] and new_state["emulatorIsRunning"]:
            print("Fading down")
            self.musicPlayer.fadeDownMusic(not self.restart)

        else:
            print("Nothing to do. Waiting...")
            time.sleep(2)

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
