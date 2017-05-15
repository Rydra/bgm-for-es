from unittest import TestCase
from mock import MagicMock
from mock import PropertyMock
import os
import mock

from src.bgm import Application


class BgmShould(TestCase):
    def test_playMusicIfEmulatorStationIsRunning(self):
        vals = {
            "emulationstatio": True
        }

        def processMock(procName):
            if procName in vals:
                return vals[procName]

            return False

        processService = MagicMock()
        processService.processIsRunning = MagicMock(side_effect=processMock)
        processService.anyProcessIsRunning = MagicMock(return_value=False)

        processService.findPid = MagicMock(return_vale=-1)

        os.listdir = MagicMock(return_value=['file1.ogg', 'file2.ogg', 'file3.ogg'])
        os.path.exists = MagicMock(return_value=False)

        musicPlayer = MagicMock()
        musicPlayer.isPlaying = False

        os.listdir('/home/pi/RetroPie/music')

        previousState = {"emulatorIsRunning": False}
        Application(processService, musicPlayer).executeState(previousState)

        args, kwargs = musicPlayer.playSong.call_args
        self.assertTrue(args[0] in [os.path.join('/home/pi/RetroPie/music', 'file1.ogg'),
                                    os.path.join('/home/pi/RetroPie/music', 'file2.ogg'),
                                    os.path.join('/home/pi/RetroPie/music', 'file3.ogg')])
        musicPlayer.playSong.assert_called_once()

# if __name__ == '__main__':
#    unittest.main()
