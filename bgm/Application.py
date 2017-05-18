from State import *


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

        self.currentState = self.getInitialState()

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

        self.currentState = self.currentState.nextState(self.getState())
        self.currentState.run()

    def run(self):

        # Delay audio start per config option above
        if self.startdelay > 0:
            time.sleep(self.startdelay)

        self.waitomxPlayer()

        while True:
            self.executeState()