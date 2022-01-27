import os
import random
import secrets
import time
from enum import Enum
from queue import LifoQueue, Queue
from typing import List, Optional

from confuse import Configuration
from transitions import Machine

from bgm.music_player import MusicPlayer
from bgm.process_service import ProcessService


class MusicState(Enum):
    PAUSED = "paused"
    STOPPED = "stopped"
    PLAYING_MUSIC = "playing_music"


class MusicStateMachine:
    random.seed()

    class _EnvironmentState:
        def __init__(
            self,
            music_is_disabled: bool,
            es_running: bool,
            emulator_is_running: bool,
            song_is_being_played: bool,
            restart: bool,
        ) -> None:
            self.restart = restart
            self.song_is_being_played = song_is_being_played
            self.stopper_process_is_running = emulator_is_running
            self.main_process_running = es_running
            self.music_is_disabled = music_is_disabled

    def __init__(
        self,
        process_service: ProcessService,
        music_player: MusicPlayer,
        config: Configuration,
        forced_initial_status: Optional[MusicState] = None,
    ):
        self._process_service = process_service
        self._music_player = music_player

        self._startdelay = config["startdelay"].get()
        self._musicdir = config["musicdir"].as_filename()
        self._restart = config["restart"].get()
        self._startsong = config["startsong"].get()

        self._song_queue = self._generate_random_music_queue()

        self._mainprocess = config["mainprocess"].get()
        self._stopper_processes = config["emulator_names"].get()

        self._machine = Machine(
            model=self, states=MusicState, initial=forced_initial_status or self._get_initial_state()
        )
        self._machine.add_transition(
            "run_trns", MusicState.PAUSED, MusicState.STOPPED, before="stop_music", conditions="has_to_stop_music"
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.PAUSED,
            MusicState.PLAYING_MUSIC,
            before="fade_up",
            conditions="stopper_process_is_not_running",
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.STOPPED,
            MusicState.PLAYING_MUSIC,
            before="play_music",
            conditions="has_to_play_music",
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.PLAYING_MUSIC,
            MusicState.STOPPED,
            before="stop_music",
            conditions="has_to_stop_music",
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.PLAYING_MUSIC,
            MusicState.PAUSED,
            before="fade_down",
            conditions="should_fade_down_and_pause",
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.PLAYING_MUSIC,
            MusicState.STOPPED,
            before="fade_down",
            conditions="should_fade_down_and_stop",
        )
        self._machine.add_transition(
            "run_trns",
            MusicState.PLAYING_MUSIC,
            MusicState.PLAYING_MUSIC,
            before="play_music",
            conditions="_music_is_not_playing",
        )

    def execute_state(self) -> None:
        state = self._get_state()
        self.run_trns(state)  # type: ignore

    def run(self) -> None:
        if self._startdelay > 0:
            time.sleep(self._startdelay)

        self._wait_splash_screen()

        while True:
            self.execute_state()
            time.sleep(2)

    def _get_songs(self) -> List[str]:
        return [song for song in os.listdir(self._musicdir) if song[-4:] == ".mp3" or song[-4:] == ".ogg"]

    def _generate_random_music_queue(self) -> Queue:
        song_queue: Queue[str] = LifoQueue()
        song_list = self._get_songs()

        if self._startsong in song_list:
            song_queue.put(self._startsong)
            song_list.remove(self._startsong)

        while len(song_list) > 0:
            song_to_add = secrets.randbelow(len(song_list) - 1)
            song_queue.put(song_list[song_to_add])
            song_list.remove(song_list[song_to_add])

        return song_queue

    # ACTIONS

    def delay(self) -> None:
        time.sleep(2)

    def stop_music(self, status: _EnvironmentState) -> None:
        self._music_player.stop()

    def fade_up(self, status: _EnvironmentState) -> None:
        self._music_player.fade_up_music()

    def fade_down(self, status: _EnvironmentState) -> None:
        self._music_player.fade_down_music(not self._restart)

    def play_music(self, status: _EnvironmentState) -> None:
        if self._song_queue.empty():
            self._song_queue = self._generate_random_music_queue()

        song = os.path.join(self._musicdir, self._song_queue.get())
        self._music_player.play_song(song)

    # CONDITIONS

    def has_to_stop_music(self, status: _EnvironmentState) -> bool:
        return not status.stopper_process_is_running and (status.music_is_disabled or not status.main_process_running)

    def stopper_process_is_not_running(self, status: _EnvironmentState) -> bool:
        return not status.stopper_process_is_running

    def should_fade_down_and_stop(self, status: _EnvironmentState) -> bool:
        return status.stopper_process_is_running and self._restart

    def should_fade_down_and_pause(self, status: _EnvironmentState) -> bool:
        return status.stopper_process_is_running and not self._restart

    def has_to_play_music(self, status: _EnvironmentState) -> bool:
        return status.main_process_running and not status.stopper_process_is_running

    def _music_is_not_playing(self, status: _EnvironmentState) -> bool:
        return not self._music_player.is_playing

    def _get_initial_state(self) -> MusicState:
        if self._music_player.is_playing:
            return MusicState.PLAYING_MUSIC
        elif self._music_player.is_paused:
            return MusicState.PAUSED
        else:
            return MusicState.STOPPED

    def _get_state(self) -> _EnvironmentState:
        status = self._EnvironmentState(
            emulator_is_running=self._process_service.any_process_is_running(self._stopper_processes),
            es_running=self._process_service.process_is_running(self._mainprocess),
            music_is_disabled=self._music_is_disabled(),
            restart=self._restart,
            song_is_being_played=self._music_player.is_playing,
        )

        return status

    def _music_is_disabled(self) -> bool:
        return os.path.exists("/home/pi/PyScripts/DisableMusic")

    def _wait_splash_screen(self) -> None:
        # Look for OMXplayer - if it's running, someone's got a splash screen going!
        while self._process_service.process_is_running("omxplayer") or self._process_service.process_is_running(
            "omxplayer.bin"
        ):
            time.sleep(1)
