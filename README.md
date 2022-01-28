# Background Music for EmulationStation

A python script to run background music in EmulationStation for Retropie,
inspired by the script posted [here](https://retropie.org.uk/forum/topic/347/background-music-continued-from-help-support),
but focusing on a script with well-written code, trying to follow good design practices
and putting special attention on testability

## Installing BGM for EmulationStation

_Prerrequisites_: python >=3.7 is required to install this application. You can check your version
by executing this command on your machine:

```
python --version
```

or

```
python3 --version
```

Enter the RetroPie console (you can reach it by pressing the F4 key when EmulationStation
is running) and run the following commands:

```
curl -sSL https://raw.githubusercontent.com/Rydra/bgm-for-es/main/scripts/install-esbgm.py | python3 -
```

After installing, reboot the machine:

```
sudo reboot
```

## Uninstalling BGM for EmulationStation

```
curl -sSL https://raw.githubusercontent.com/Rydra/bgm-for-es/main/scripts/install-esbgm.py > install-esbgm.py
python3 install-esbgm.py --uninstall
```

## Enabling/Disabling the background music

Under the config section of EmulationStation two new commands have been added:

- Enable background music
- Disable background music

Select one or the other to enable or disable the background music

## How it works

Place your music in .mp3 or .ogg format in the folder that will be created in `/home/pi/RetroPie/music`.
You can change the folder where you place your music in the config file (see _Configuration_ section).
Once you reboot and the script
starts, a default config file will be created at `/home/pi/.config/esbgm/config.yaml`

If you want to manually execute the application you can execute the following command:

```
esbgm
```

## Configuration

The configuration file that you may find in `/home/pi/.config/esbgm/config.yaml` (it will appear
once you start the `esbgm` script for the first time) contains the following content:

```yaml
# Value (in seconds) to delay audio start.  If you have a splash screen with audio and the script is playing music over the top of it, increase this value to delay the script from starting.
startdelay: 0

# The directory where you will place your music in .mp3 or .ogg format
musicdir: ~/RetroPie/music

# Whether the music should restart upon unpausing or resume
# from where it was left out.
restart: true
startsong:

# The main process. Upon starting this process, the music will start playing...
mainprocess: emulationstatio

# unless one of these processes is running, then the music will fade out
# until only the mainprocess is running again
emulator_names:
  - retroarch
  - ags
  - uae4all2
  - uae4arm
  - capricerpi
  - linapple
  - hatari
  - stella
  - atari800
  - xroar
  - vice
  - daphne
  - reicast
  - pifba
  - osmose
  - gpsp
  - jzintv
  - basiliskll
  - mame
  - advmame
  - dgen
  - openmsx
  - mupen64plus
  - gngeo
  - dosbox
  - ppsspp
  - simcoupe
  - scummvm
  - snes9x
  - pisnes
  - frotz
  - fbzx
  - fuse
  - gemrb
  - cgenesis
  - zdoom
  - eduke32
  - lincity
  - love
  - kodi
  - alephone
  - micropolis
  - openbor
  - openttd
  - opentyrian
  - cannonball
  - tyrquake
  - ioquake3
  - residualvm
  - xrick
  - sdlpop
  - uqm
  - stratagus
  - wolf4sdl
  - solarus
```

Description of the settings:

| Option         | Default value            | Description                                                                                               |
| -------------- | ------------------------ | --------------------------------------------------------------------------------------------------------- |
| startdelay     | 0                        | How much time in second you want to wait once EmulationStation starts before playing the first song       |
| musicdir       | /home/pi/RetroPie/music  | The directory where the music is placed and where it should be played                                     |
| restart        | True                     | If True, resets the song from the beginning upon resuming                                                 |
| startsong      | Empty                    | The exact name of the song you want to play in first place. Leave empty to let the player decide randomly |
| mainprocess    | emulationstatio          | The name of the process which, when running, music will play                                              |
| emulator_names | list of common emulators | The name of the processes which, when running, music will pause/stop                                      |
