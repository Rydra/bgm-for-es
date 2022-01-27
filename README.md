# Background Music for EmulationStation

A python script to run background music in EmulationStation for Retropie, inspired by the script posted in https://retropie.org.uk/forum/topic/347/background-music-continued-from-help-support, but focusing on a script with well-written code, trying to follow good design practices and putting special attention on testability

## How to install

Enter the RetroPie console (you can reach it by pressing the F4 key when EmulationStation is running) and run the following commands:

```bash
sudo sh -c 'echo "deb [trusted=yes] https://repo.fury.io/rydra/ /" > /etc/apt/sources.list.d/es-bgm.list'
sudo apt update
sudo apt install python-pygame python-es-bgm
```

These commands will update your sources and install the python-es-bgm package which will run your music. Afterwards, place your music in the music folder (as described in the _How it works_ section and either restart EmulationStation or reboot your Raspberry. Enjoy your new EmulationStation with background music.

```bash
sudo reboot
```

After the reboot, a daemon service called `bgm` will be running in the background, playing your music when EmulationStation is actively running and fading down when you start an emulator.

NEW METHOD

```
curl -sSL https://raw.githubusercontent.com/Rydra/bgm-for-es/main/scripts/install-esbgm.py | python3 -
```

## How it works

Place your music in .mp3 or .ogg format in the folder that will be created in `/home/pi/RetroPie/roms/music`. You can change the folder where you place your music in the settings.

If you want to manually execute the application you can execute the following command:

## Configuration

The configuration file that you may find in `/etc/bgmconfig.ini` contains the following content:

```
[default]
startdelay = 0
musicdir = /home/pi/RetroPie/roms/music
restart = True
startsong =
```

| Option     | Default value                | Description                                                                                               |
| ---------- | ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| startdelay | 0                            | How much time in second you want to wait once EmulationStation starts before playing the first song       |
| musicdir   | /home/pi/RetroPie/roms/music | How much time in second you want to wait once EmulationStation starts before playing the first song       |
| restart    | True                         | How much time in second you want to wait once EmulationStation starts before playing the first song       |
| startsong  | Empty                        | The exact name of the song you want to play in first place. Leave empty to let the player decide randomly |

If you want to override these settings, you can create a file in your personal folder called `.bgmconfig.ini` (so, in the path `~/.bgmconfig.ini`) containing `[default]` in the first line and override any option you want.

## How to create a debian package from this source code

There is a make task that will do this job for you:

```
make debian-package
```
