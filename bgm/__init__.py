import argparse

import confuse

from bgm.music_player import MusicPlayer
from bgm.music_state_machine import MusicStateMachine
from bgm.process_service import ProcessService


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse arguments for debugging purposes")
    parser.add_argument("-es", nargs="?", help="the process name for emulationstation")
    parser.add_argument(
        "-names",
        metavar="ENames",
        type=str,
        nargs="*",
        help="the emulator names you want to consider",
    )

    args = parser.parse_args()
    config = confuse.Configuration("esbgm", __name__)
    config.set_args(args, dots=True)
    print("configuration directory is", config.config_dir())
    MusicStateMachine(ProcessService(), MusicPlayer(), config).run()


if __name__ == "__main__":
    main()
