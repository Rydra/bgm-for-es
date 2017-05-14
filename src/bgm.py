import os
import random
import time
from Queue import LifoQueue

from MusicPlayer import MusicPlayer
from ProcessService import ProcessService

class Application:
    random.seed()

    def __init__(self, processService, musicPlayer):
        self.processService = processService
        self.musicPlayer = musicPlayer

        self.startdelay = 0  # Value (in seconds) to delay audio start.  If you have a splash screen with audio and the script is playing music over the top of it, increase this value to delay the script from starting.
        self.musicdir = '/home/pi/RetroPie/music'

        self.restart = True  # If true, this will cause the script to fade the music out and -stop- the song rather than pause it.
        self.startsong = ""  # if this is not blank, this is the EXACT, CaSeSeNsAtIvE filename of the song you always want to play first on boot.

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

        songQueue = LifoQueue()

        songList = self.getSongs()

        # Check for a starting song
        if self.startsong in songList:
            songQueue.put(self.startsong)
            songList.remove(self.startsong)

        while len(songList) > 0:
            songToAdd = random.randint(0, len(songList) - 1)
            songQueue.put(songList[songToAdd])
            songList.remove(songList[songToAdd])

        return songQueue

    def updateState(self):

        state = {
            "musicIsDisabled": self.musicIsDisabled(),
            "esRunning": self.processService.processIsRunning("emulationstatio"),
            "emulatorIsRunning": self.processService.anyProcessIsRunning(self.emulatornames),
            "songIsBeingPlayed": self.musicPlayer.isPlaying
        }

        return state

    def waitForProcess(self, processName):
        while not self.processService.processIsRunning(processName):
            time.sleep(1)

    def musicIsDisabled(self):
        return os.path.exists('/home/pi/PyScripts/DisableMusic')

    def playNewSongIfSilent(self):
        if not self.musicPlayer.isPlaying:

            if self.songQueue.empty():
                self.songQueue = self.getRandomQueue()

            song = os.path.join(self.musicdir, self.songQueue.get())
            self.musicPlayer.playSong(song)

            print("BGM Now Playing: " + song)

    def waitomxPlayer(self):
        # Look for OMXplayer - if it's running, someone's got a splash screen going!

        omxplayerPid = self.processService.findPid("omxplayer")
        if omxplayerPid != -1:
            while os.path.exists('/proc/' + omxplayerPid):
                time.sleep(1)  # OMXPlayer is running, sleep 1 to prevent the need for a splash.

        omxplayerPid = self.processService.findPid("omxplayer.bin")
        if omxplayerPid != -1:
            while os.path.exists('/proc/' + omxplayerPid):
                time.sleep(1)

    def run(self):

        # Delay audio start per config option above
        if self.startdelay > 0:
            time.sleep(self.startdelay)

        self.waitomxPlayer()

        state = self.updateState()
        while True:
            newstate = self.updateState()

            if not newstate["esRunning"]:
                print("esNotRunning")

            if not self.restart and state["emulatorIsRunning"] and not newstate["emulatorIsRunning"]:
                print("Fading up")
                self.musicPlayer.fadeUpMusic(self.restart)

            elif newstate["musicIsDisabled"] or (not newstate["esRunning"] and not newstate["emulatorIsRunning"]):
                print("Music disabled! Stop")
                self.musicPlayer.stop()

            elif newstate["esRunning"] and not newstate["emulatorIsRunning"]:
                print("I'm playing a song")
                self.playNewSongIfSilent()

            elif newstate["songIsBeingPlayed"] and newstate["emulatorIsRunning"]:
                print("Fading down")
                self.musicPlayer.fadeDownMusic(self.restart)

            else:
                print("Nothing to do. Waiting...")

            state = newstate
            time.sleep(2)

        print("An error has occurred that has stopped Test1.py from executing.")


if __name__ == '__main__':
    Application(ProcessService(), MusicPlayer()).run()
