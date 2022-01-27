from setuptools import setup

setup(
    name="es-bgm",
    version="1.0.1",
    packages=["bgm"],
    url="",
    license="GPL",
    package_data={"bgm": ["bgmconfig.ini"]},
    author="David Jimenez",
    author_email="davigetto@gmail.com",
    description="Allows you to add background music to EmulationStation",
    requires=["pytest"],
    entry_points={"console_scripts": ["es-bgm = bgm:main"]},
    data_files=[
        ("/lib/systemd/system", ["service/bgm.service"]),
        ("/etc", ["cfg/bgmconfig.ini"]),
        ("/home/pi/RetroPie/roms/music", ["extra/PLACE_YOUR_MUSIC_HERE"]),
    ],
)
