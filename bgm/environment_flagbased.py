import os
from pathlib import Path

from bgm.environment import BaseEnvironment, EnvironmentState
from bgm.music_player import MusicPlayer
from bgm.process_service import ProcessService


class FlagBasedEnvironment(BaseEnvironment):
    """
    Manages and tracks the environment so that the state machine can make decisions on what to do next
    """

    def __init__(
        self, process_service: ProcessService, music_player: MusicPlayer, restart: bool, mainprocess: str
    ) -> None:
        super().__init__(restart)
        self._mainprocess = mainprocess
        self._process_service = process_service
        self._music_player = music_player

    def _music_is_disabled(self) -> bool:
        return os.path.exists(os.path.expanduser("~/.config/esbgm/disable.flag"))

    def get_state(self) -> EnvironmentState:
        status = EnvironmentState(
            stopper_process_is_running=self._shouldstop(),
            main_process_running=self._process_service.process_is_running(self._mainprocess),
            music_is_disabled=self._music_is_disabled(),
            restart=self._restart,
            song_is_being_played=self._music_player.is_playing,
        )

        return status

    def _shouldstop(self) -> bool:
        path = Path(os.path.expanduser("~/.musicpaused.flag"))
        return path.exists()
