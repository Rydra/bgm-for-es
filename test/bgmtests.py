import unittest
from mock import MagicMock

from bgm import Application


class BgmShould(unittest.TestCase):
    
    def a(self):

        vals = {
            "emustation": True
        }

        def processMock(procName):
            if procName in vals:
                return vals[procName]

            return False

        processService = MagicMock()
        processService.processIsRunning = MagicMock(side_effect=processMock)

        app = Application()
        

if __name__ == '__main__':
    unittest.main()
