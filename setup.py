from distutils.core import setup

__author__ = 'nik'

setup(
    name="i2Ctemp-app-demo",
    version="1.0",
    author="Nicola La Gloria",
    url="http://warpx.io",
    scripts=['pyi2Ctemp.py'],
    data_files=[('resources', ['resources/weather_icons.png', 'resources/effra-regular.ttf'])]
)
