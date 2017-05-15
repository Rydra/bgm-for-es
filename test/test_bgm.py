from unittest import TestCase
from mock import MagicMock
import os

from src.bgm import Application


class BgmShould(TestCase):

    def test_playMusicIfEmulatorStationIsRunning(self):

        scenarioMaker = self._ScenarioMaker()
        app = scenarioMaker\
            .theFollowingProcessesAreRunning("emulationstatio")\
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg'])\
            .build()

        previousState = {"emulatorIsRunning": False}
        app.executeState(previousState)

        scenarioMaker.assertASongFromTheDirectoryIsBeingPlayed(self)

    def test_fadeDownMusicIfEmulatorHasStartedAndASongIsBeingPlayed(self):
        scenarioMaker = self._ScenarioMaker()
        app = scenarioMaker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .anEmulatorIsRunning()\
            .aSongIsBeingPlayed()\
            .build()

        previousState = {"emulatorIsRunning": False}
        app.executeState(previousState)

        scenarioMaker.assertMusicHasFadeDown()

    def test_fadeUpMusicIfEmulatorIsNotRunningAndEmulationStationIsRunningAndMusicIsPaused(self):
        scenarioMaker = self._ScenarioMaker()
        app = scenarioMaker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .aSongIsPaused()\
            .build()

        previousState = {"emulatorIsRunning": False}
        app.executeState(previousState)

        scenarioMaker.assertMusicHasFadeUp()

    class _ScenarioMaker():

        def __init__(self):
            self.processService = MagicMock()
            self.processService.anyProcessIsRunning = MagicMock(return_value=False)
            self.processService.findPid = MagicMock(return_vale=-1)

            self.musicPlayer = MagicMock()
            self.musicPlayer.isPlaying = False
            self.musicPlayer.isPaused = False
            os.path.exists = MagicMock(return_value=False)

        def aSongIsBeingPlayed(self):
            self.musicPlayer.isPlaying = True
            return self

        def theFollowingProcessesAreRunning(self, *processes):
            self.processService.processIsRunning = MagicMock(side_effect=lambda x: x in processes)
            return self

        def anEmulatorIsRunning(self):
            self.processService.anyProcessIsRunning = MagicMock(return_value=True)
            return self

        def build(self):
            return Application(self.processService, self.musicPlayer)

        def theFollowingSongsArePresent(self, songs):
            os.listdir = MagicMock(return_value=songs)
            return self

        def assertASongFromTheDirectoryIsBeingPlayed(self, test):
            args, kwargs = self.musicPlayer.playSong.call_args
            test.assertTrue(args[0] in [os.path.join('/home/pi/RetroPie/music', 'file1.ogg'),
                                        os.path.join('/home/pi/RetroPie/music', 'file2.ogg'),
                                        os.path.join('/home/pi/RetroPie/music', 'file3.ogg')])
            self.musicPlayer.playSong.assert_called_once()

        def assertMusicHasFadeDown(self):
            self.musicPlayer.fadeDownMusic.assert_called_once()

        def aSongIsPaused(self):
            self.musicPlayer.isPaused = True
            return self

        def assertMusicHasFadeUp(self):
            self.musicPlayer.fadeUpMusic.assert_called_once()


