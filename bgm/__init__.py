import os
from ConfigParser import SafeConfigParser

from bgm.MusicPlayer import MusicPlayer
from bgm.ProcessService import ProcessService
from bgm.Application import Application


def main():
    config = SafeConfigParser()
    config.read(['/etc/bgmconfig.ini', os.path.expanduser('~/.bgmconfig.ini')])
    Application(ProcessService(), MusicPlayer(), config).run()
