import os
from typing import List

from bgm.music_player import MusicPlayer
from bgm.process_service import ProcessService


class EnvironmentState:
    def __init__(
        self,
        music_is_disabled: bool,
        main_process_running: bool,
        stopper_process_is_running: bool,
        song_is_being_played: bool,
        restart: bool,
    ) -> None:
        self.restart = restart
        self.song_is_being_played = song_is_being_played
        self.stopper_process_is_running = stopper_process_is_running
        self.main_process_running = main_process_running
        self.music_is_disabled = music_is_disabled


class BaseEnvironment:
    def __init__(self, restart: bool) -> None:
        self._restart = restart

    def should_fade_down_and_stop(self, state: EnvironmentState) -> bool:
        return state.stopper_process_is_running and self._restart

    def should_pause(self, state: EnvironmentState) -> bool:
        return state.stopper_process_is_running and not self._restart

    def has_to_stop_music(self, state: EnvironmentState) -> bool:
        return not state.stopper_process_is_running and (state.music_is_disabled or not state.main_process_running)

    def music_is_not_playing(self, state: EnvironmentState) -> bool:
        return not state.song_is_being_played

    def has_to_play_music(self, state: EnvironmentState) -> bool:
        return state.main_process_running and not state.stopper_process_is_running and not state.music_is_disabled

    def get_state(self) -> EnvironmentState:
        pass


class Environment(BaseEnvironment):
    """
    Manages and tracks the environment so that the state machine can make decisions on what to do next
    """

    def __init__(
        self,
        process_service: ProcessService,
        music_player: MusicPlayer,
        restart: bool,
        mainprocess: str,
        stopper_processes: List[str],
    ) -> None:

        super().__init__(restart)
        self._mainprocess = mainprocess
        self._stopper_processes = stopper_processes
        self._process_service = process_service
        self._music_player = music_player

    def get_state(self) -> EnvironmentState:
        status = EnvironmentState(
            stopper_process_is_running=self._process_service.any_process_is_running(self._stopper_processes),
            main_process_running=self._process_service.process_is_running(self._mainprocess),
            music_is_disabled=self._music_is_disabled(),
            restart=self._restart,
            song_is_being_played=self._music_player.is_playing,
        )

        return status

    def _music_is_disabled(self) -> bool:
        return os.path.exists(os.path.expanduser("~/.config/esbgm/disable.flag"))
