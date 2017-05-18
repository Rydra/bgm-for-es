import os
from unittest import TestCase

from mock import MagicMock

from bgm.Application import Application


class BgmShould(TestCase):
    def test_play_music_if_ES_is_running(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .build()

        app.executeState()

        scenario_maker.assertASongFromTheDirectoryIsBeingPlayed(self)

    def test_fade_down_music_by_pausing_if_Emulator_is_running_and_a_song_is_being_played(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .anEmulatorIsRunning() \
            .pauseOnEmulatorRun() \
            .aSongIsBeingPlayed() \
            .build()

        app.executeState()

        scenario_maker.assertMusicHasFadeDown(pause=True)

    def test_fade_down_music_by_not_pausing_if_Emulator_is_running_and_a_song_is_being_played(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .anEmulatorIsRunning() \
            .aSongIsBeingPlayed() \
            .build()

        app.executeState()

        scenario_maker.assertMusicHasFadeDown(pause=False)

    def test_fade_up_music_if_Emulator_is_not_running_and_ES_is_running_and_music_is_paused(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .aSongIsPaused() \
            .build()

        app.executeState()

        scenario_maker.assertMusicHasFadeUp()

    def test_stop_music_if_music_is_disabled(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .theMusicIsDisabled() \
            .aSongIsBeingPlayed()\
            .build()

        app.executeState()

        scenario_maker.assertMusicHasBeenStopped()

    def test_do_nothing_if_ES_is_not_running_but_emulator_isr_running(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .anEmulatorIsRunning() \
            .build()

        app.executeState()

        scenario_maker.assertNothingHasBeenDone()

    def test_stop_music_if_ES_nor_emulator_are_running(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .aSongIsBeingPlayed()\
            .build()

        app.executeState()

        scenario_maker.assertMusicHasBeenStopped()

    def test_do_nothing_if_ES_is_running_but_a_song_is_already_playing(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingProcessesAreRunning("emulationstatio") \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .aSongIsBeingPlayed() \
            .build()

        app.executeState()

        scenario_maker.assertNothingHasBeenDone()

    def test_do_nothing_if_emulator_is_running_and_silent(self):
        scenario_maker = self._ScenarioMaker()
        app = scenario_maker \
            .theFollowingSongsArePresent(['file1.ogg', 'file2.ogg', 'file3.ogg']) \
            .anEmulatorIsRunning() \
            .build()

        app.executeState()

        scenario_maker.assertNothingHasBeenDone()

    class _ScenarioMaker:
        def __init__(self):
            self.processService = MagicMock()
            self.processService.anyProcessIsRunning = MagicMock(return_value=False)
            self.processService.findPid = MagicMock(return_vale=-1)
            self.processService.processIsRunning = MagicMock(side_effect=lambda x: False)
            self.config = MagicMock()

            self.restart = True

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

        def pauseOnEmulatorRun(self):
            self.restart = False
            return self

        def aSongIsPaused(self):
            self.musicPlayer.isPaused = True
            return self

        def theFollowingSongsArePresent(self, songs):
            os.listdir = MagicMock(return_value=songs)
            return self

        def theMusicIsDisabled(self):
            os.path.exists = MagicMock(side_effect=lambda _: True)
            return self

        def build(self):
            default_config = {
                "startdelay": 0,
                "musicdir": '/home/pi/RetroPie/music',
                "restart": self.restart,
                "startsong": ""
            }

            self.config.getboolean.side_effect = lambda x, y: default_config[y]
            self.config.getint.side_effect = lambda x, y: default_config[y]
            self.config.get.side_effect = lambda x, y: default_config[y]

            return Application(self.processService, self.musicPlayer, self.config)

        def assertASongFromTheDirectoryIsBeingPlayed(self, test):
            args, kwargs = self.musicPlayer.playSong.call_args
            test.assertTrue(args[0] in [os.path.join('/home/pi/RetroPie/music', 'file1.ogg'),
                                        os.path.join('/home/pi/RetroPie/music', 'file2.ogg'),
                                        os.path.join('/home/pi/RetroPie/music', 'file3.ogg')])
            self.musicPlayer.playSong.assert_called_once()

        def assertMusicHasFadeDown(self, pause):
            self.musicPlayer.fadeDownMusic.assert_called_once_with(pause)

        def assertMusicHasFadeUp(self):
            self.musicPlayer.fadeUpMusic.assert_called_once()

        def assertMusicHasBeenStopped(self):
            self.musicPlayer.stop.assert_called_once()

        def assertNothingHasBeenDone(self):
            self.musicPlayer.stop.assert_not_called()
            self.musicPlayer.fadeUpMusic.assert_not_called()
            self.musicPlayer.fadeDownMusic.assert_not_called()
            self.musicPlayer.playSong.assert_not_called()
