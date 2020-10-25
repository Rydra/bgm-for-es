import os
from configparser import ConfigParser

from bgm.music_player import MusicPlayer
from bgm.process_service import ProcessService
from bgm.music_state_machine import MusicStateMachine

import argparse


def main():

    parser = argparse.ArgumentParser(description='Parse arguments for debugging purposes')
    parser.add_argument('-es', nargs='?', help='the process name for emulationstation')
    parser.add_argument('-names', metavar='ENames', type=str, nargs='*', help='the emulator names you want to consider')

    parsed_arguments = parser.parse_args()

    config = ConfigParser()
    config.read(['/etc/bgmconfig.ini',
                 os.path.expanduser('~/.bgmconfig.ini'),
                 os.path.expanduser('/home/pi/.bgmconfig.ini')])
    MusicStateMachine(ProcessService(), MusicPlayer(), config,
                      forced_es_process=parsed_arguments.es,
                      forced_emulators=parsed_arguments.names).run()

if __name__ == "__main__":
    main()
