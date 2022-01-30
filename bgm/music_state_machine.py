import os
import random
import secrets
import time
from enum import Enum
from queue import LifoQueue, Queue
from typing import List, Optional

from confuse import Configuration
from transitions import Machine

from bgm.environment import BaseEnvironment, EnvironmentState
from bgm.music_player import MusicPlayer
from bgm.process_service import ProcessService


class MusicState(Enum):
    PAUSED = "paused"
    STOPPED = "stopped"
    PLAYING_MUSIC = "playing_music"


class MusicStateMachine:
    """
    The state machine is responsible to orchestrate
    the calls to the music player, based on the information
    provided by the environment
    """

    random.seed()

    def __init__(
        self,
        process_service: ProcessService,
        music_player: MusicPlayer,
        config: Configuration,
        environment: BaseEnvironment,
        forced_initial_status: Optional[MusicState] = None,
    ):
        self._process_service = process_service
        self._music_player = music_player
        self.environment = environment

        self._startdelay = config["startdelay"].get()
        self._musicdir = config["musicdir"].as_filename()
        self._restart = config["restart"].get()
        self._startsong = config["startsong"].get()

        self._song_queue = self._generate_random_music_queue()

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
            conditions="has_to_play_music",
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
            conditions="should_pause",
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
            conditions="music_is_not_playing",
        )

    def execute_state(self) -> None:
        state = self.environment.get_state()
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
            song_to_add = secrets.randbelow(len(song_list))
            song_queue.put(song_list[song_to_add])
            song_list.remove(song_list[song_to_add])

        return song_queue

    # ACTIONS
    def delay(self) -> None:
        time.sleep(2)

    def stop_music(self, status: EnvironmentState) -> None:
        print("Stopping music")
        self._music_player.stop()

    def fade_up(self, status: EnvironmentState) -> None:
        self._music_player.fade_up_music()

    def fade_down(self, status: EnvironmentState) -> None:
        self._music_player.fade_down_music(not self._restart)

    def play_music(self, status: EnvironmentState) -> None:
        if self._song_queue.empty():
            self._song_queue = self._generate_random_music_queue()

        song = os.path.join(self._musicdir, self._song_queue.get())
        print(f"Playing {song}")
        self._music_player.play_song(song)

    # CONDITIONS
    def has_to_stop_music(self, status: EnvironmentState) -> bool:
        return self.environment.has_to_stop_music(status)

    def has_to_play_music(self, status: EnvironmentState) -> bool:
        return self.environment.has_to_play_music(status)

    def should_fade_down_and_stop(self, status: EnvironmentState) -> bool:
        return self.environment.should_fade_down_and_stop(status)

    def should_pause(self, status: EnvironmentState) -> bool:
        return self.environment.should_pause(status)

    def music_is_not_playing(self, state: EnvironmentState) -> bool:
        return self.environment.music_is_not_playing(state)

    def _get_initial_state(self) -> MusicState:
        if self._music_player.is_playing:
            return MusicState.PLAYING_MUSIC
        elif self._music_player.is_paused:
            return MusicState.PAUSED
        else:
            return MusicState.STOPPED

    def _wait_splash_screen(self) -> None:
        # Look for OMXplayer - if it's running, someone's got a splash screen going!
        while self._process_service.process_is_running("omxplayer") or self._process_service.process_is_running(
            "omxplayer.bin"
        ):
            time.sleep(1)
