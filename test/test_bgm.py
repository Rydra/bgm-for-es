from unittest import TestCase
from mock import MagicMock
from mock import PropertyMock
import os
import mock

from src.bgm import Application


class BgmShould(TestCase):

    def test_playMusicIfEmulatorStationIsRunning(self):

        musicPlayer = MagicMock()
        app = self._ScenarioMaker(musicPlayer)\
            .theFollowingProcessesAreRunning("emulationstatio")\
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg'])\
            .build()

        previousState = {"emulatorIsRunning": False}
        app.executeState(previousState)

        args, kwargs = musicPlayer.playSong.call_args
        self.assertTrue(args[0] in [os.path.join('/home/pi/RetroPie/music', 'file1.ogg'),
                                    os.path.join('/home/pi/RetroPie/music', 'file2.ogg'),
                                    os.path.join('/home/pi/RetroPie/music', 'file3.ogg')])
        musicPlayer.playSong.assert_called_once()


    class _ScenarioMaker():

        def __init__(self, musicPlayer):
            self.processService = MagicMock()
            self.processService.anyProcessIsRunning = MagicMock(return_value=False)
            self.processService.findPid = MagicMock(return_vale=-1)

            self.musicPlayer = musicPlayer
            self.musicPlayer.isPlaying = False
            os.path.exists = MagicMock(return_value=False)

        def aSongIsBeingPlayed(self):
            self.musicPlayer.isPlaying = True
            return self

        def theFollowingProcessesAreRunning(self, *processes):
            def processMock(procName):
                if procName in processes:
                    return True

                return False

            self.processService.processIsRunning = MagicMock(side_effect=processMock)
            return self

        def anEmulatorRunning(self):
            self.processService.anyProcessIsRunning = MagicMock(return_value=True)
            return self

        def build(self):
            return Application(self.processService, self.musicPlayer)

        def theFollowingSongsArePresent(self, songs):
            os.listdir = MagicMock(return_value=songs)
            return self


