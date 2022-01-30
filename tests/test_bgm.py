import os
from typing import List

import confuse
import pytest
from bunch import Bunch
from doublex import ANY_ARG, Spy, assert_that, called
from hamcrest import *
from pytest_mock import MockerFixture

from bgm import Environment, MusicPlayer, ProcessService
from bgm.music_state_machine import MusicState, MusicStateMachine


@pytest.fixture
def testcontext():
    return Bunch(forced_state=None)


@pytest.fixture
def process_service_spy() -> ProcessService:
    with Spy(ProcessService) as process_service:
        process_service.any_process_is_running(ANY_ARG).returns(False)
        process_service.find_pid(ANY_ARG).returns(-1)
        process_service.process_is_running(ANY_ARG).returns(False)

    return process_service


@pytest.fixture
def music_player_spy() -> MusicPlayer:
    with Spy(MusicPlayer) as music_player:
        music_player.is_playing.returns(False)
        music_player.is_paused.returns(False)

    return music_player


@pytest.fixture
def default_config(shared_datadir):
    config = confuse.Configuration("testapp")
    config.set_file(shared_datadir / "config_test.yaml")
    return config


def build_env(config, process_service, music_player):
    restart = config["restart"].get()
    stopper_processes = config["emulator_names"].get()
    mainprocess = config["mainprocess"].get()
    environment = Environment(process_service, music_player, restart, mainprocess, stopper_processes)

    return environment


class TestBgm:
    def test_play_music_if_ES_is_running(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )

        app.execute_state()
        assert_that(app.state, is_(MusicState.PLAYING_MUSIC))
        assert_that(
            music_player_spy.play_song,
            called().with_args(
                is_in(
                    [
                        os.path.join("/home/pi/RetroPie/music", "file1.ogg"),
                        os.path.join("/home/pi/RetroPie/music", "file2.ogg"),
                        os.path.join("/home/pi/RetroPie/music", "file3.ogg"),
                    ]
                )
            ),
        )

    def test_fade_down_music_by_pausing_if_Emulator_is_running_and_a_song_is_being_played(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        an_emulator_is_running("snes9x", testcontext)
        a_song_is_being_played(testcontext)

        default_config["restart"] = False

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()
        assert_that(app.state, is_(MusicState.PAUSED))
        assert_that(music_player_spy.fade_down_music, called().with_args(True))

    def test_fade_down_music_by_not_pausing_if_Emulator_is_running_and_a_song_is_being_played(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        an_emulator_is_running("snes9x", testcontext)
        a_song_is_being_played(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()

        assert_that(app.state, is_(MusicState.STOPPED))
        assert_that(music_player_spy.fade_down_music, called().with_args(False))

    def test_fade_up_music_if_stopper_process_is_not_running_and_ES_is_running_and_music_is_paused(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        a_song_is_paused(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()

        assert_that(app.state, is_(MusicState.PLAYING_MUSIC))
        assert_that(music_player_spy.fade_up_music, called())

    def test_play_another_song_if_song_has_ended(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        music_was_being_played(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()

        assert_that(app.state, is_(MusicState.PLAYING_MUSIC))
        assert_that(
            music_player_spy.play_song,
            called().with_args(
                is_in(
                    [
                        os.path.join("/home/pi/RetroPie/music", "file1.ogg"),
                        os.path.join("/home/pi/RetroPie/music", "file2.ogg"),
                        os.path.join("/home/pi/RetroPie/music", "file3.ogg"),
                    ]
                )
            ),
        )

    def test_stop_music_if_music_is_disabled(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        the_music_is_disabled(mocker, testcontext)
        a_song_is_being_played(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()
        assert_that(app.state, is_(MusicState.STOPPED))
        assert_that(music_player_spy.stop, called())

    def test_do_nothing_if_ES_is_not_running_but_emulator_is_running(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        an_emulator_is_running("snes9x", testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()
        assert_that(app.state, is_(MusicState.STOPPED))
        assert_that(music_player_spy.stop, not_(called()))
        assert_that(music_player_spy.fade_up_music, not_(called()))
        assert_that(music_player_spy.fade_down_music, not_(called()))
        assert_that(music_player_spy.play_song, not_(called()))

    def test_stop_music_if_ES_nor_emulator_are_running(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        a_song_is_being_played(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()
        assert_that(app.state, is_(MusicState.STOPPED))
        assert_that(music_player_spy.stop, called())

    def test_do_nothing_if_ES_is_running_but_a_song_is_already_playing(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_processes_are_running(["emulationstatio"], testcontext)
        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        a_song_is_being_played(testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(process_service_spy, music_player_spy, default_config, environment)
        app.execute_state()
        assert_that(app.state, is_(MusicState.PLAYING_MUSIC))
        assert_that(music_player_spy.stop, not_(called()))
        assert_that(music_player_spy.fade_up_music, not_(called()))
        assert_that(music_player_spy.fade_down_music, not_(called()))
        assert_that(music_player_spy.play_song, not_(called()))

    def test_do_nothing_if_emulator_is_running_and_silent(
        self, testcontext, process_service_spy, music_player_spy, default_config, mocker
    ):
        testcontext.process_service = process_service_spy
        testcontext.music_player = music_player_spy

        the_following_songs_are_present(mocker, ["file1.ogg", "file2.ogg", "file3.ogg"], testcontext)
        an_emulator_is_running("snes9x", testcontext)

        environment = build_env(default_config, process_service_spy, music_player_spy)
        app = MusicStateMachine(
            process_service_spy, music_player_spy, default_config, environment, testcontext.forced_state
        )
        app.execute_state()
        assert_that(app.state, is_(MusicState.STOPPED))
        assert_that(music_player_spy.stop, not_(called()))
        assert_that(music_player_spy.fade_up_music, not_(called()))
        assert_that(music_player_spy.fade_down_music, not_(called()))
        assert_that(music_player_spy.play_song, not_(called()))


def a_song_is_being_played(ctx):
    with ctx.music_player:
        ctx.music_player.is_playing.returns(True)


def the_following_processes_are_running(processes: List[str], ctx):
    with ctx.process_service:
        ctx.process_service.process_is_running(ANY_ARG).delegates(lambda x: x in processes)


def an_emulator_is_running(emulationprocess_name: str, ctx):
    with ctx.process_service:
        ctx.process_service.any_process_is_running(has_item(emulationprocess_name)).returns(True)
    return ctx


def a_song_is_paused(ctx):
    with ctx.music_player:
        ctx.music_player.is_paused.returns(True)


def the_following_songs_are_present(mocker: MockerFixture, songs: List[str], ctx):
    mocker.patch("bgm.music_state_machine.os.listdir").return_value = songs


def the_music_is_disabled(mocker: MockerFixture, ctx):
    mocker.patch("bgm.music_state_machine.os.path.exists").return_value = True
    return ctx


def music_was_being_played(ctx):
    ctx.forced_state = MusicState.PLAYING_MUSIC
    return ctx
