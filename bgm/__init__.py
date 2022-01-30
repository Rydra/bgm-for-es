import argparse
import os
from pathlib import Path

import confuse

from bgm.environment import BaseEnvironment, Environment
from bgm.environment_flagbased import FlagBasedEnvironment
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
    userconfig_path = os.path.join(config.config_dir(), confuse.CONFIG_FILENAME)
    if not os.path.exists(userconfig_path):
        print(f"config file not found, dumping defaults at {userconfig_path}")
        yaml = config.dump()
        with open(userconfig_path, "w") as fs:
            fs.write(yaml)

    restart = config["restart"].get()
    mainprocess = config["mainprocess"].get()
    process_service = ProcessService()
    music_player = MusicPlayer()

    is_retropie = Path("/opt/retropie/configs/all")
    environment: BaseEnvironment
    if is_retropie.exists():
        environment = FlagBasedEnvironment(process_service, music_player, restart, mainprocess)
    else:
        stopper_processes = config["emulator_names"].get()
        environment = Environment(process_service, music_player, restart, mainprocess, stopper_processes)

    MusicStateMachine(process_service, music_player, config, environment).run()


if __name__ == "__main__":
    main()
