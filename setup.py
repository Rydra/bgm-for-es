from distutils.core import setup

setup(
    name='es-bgm',
    version='1.0',
    packages=['bgm'],
    url='',
    license='GPL',
    package_data={'bgm': ['bgmconfig.ini']},
    scripts=['startbgm'],
    author='David Jimenez',
    author_email='davigetto@gmail.com',
    description='Allows you to add background music to EmulationStation',
    requires=['mock'],
    data_files=[('/etc/init.d', ['bgm.d']),
                ('/etc', ['cfg/bgmconfig.ini'])]
)
