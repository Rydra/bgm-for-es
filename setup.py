from setuptools import setup
import unittest


def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test', pattern='test_*.py')
    return test_suite

setup(
    name='es-bgm',
    version='1.0',
    packages=['bgm'],
    url='',
    license='GPL',
    package_data={'bgm': ['bgmconfig.ini']},
    author='David Jimenez',
    author_email='davigetto@gmail.com',
    description='Allows you to add background music to EmulationStation',
    requires=['mock', 'pytest'],
    entry_points=
    {'console_scripts':
         ['startbgm = bgm:main']
     },
    test_suite='setup.get_test_suite',
    data_files=[('/lib/systemd/system', ['service/bgm.service']),
                ('/etc', ['cfg/bgmconfig.ini']),
                ('/home/pi/RetroPie/roms/music', ['extra/PLACE_YOUR_MUSIC_HERE'])]
)
