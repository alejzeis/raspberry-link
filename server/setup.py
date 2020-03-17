#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink_server',
  version='1.0.0-pre',
  description='Raspberrylink Smart-car system for Raspberry Pi - Controller Software',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=['raspberrylink_server'],
  install_requires=['flask', 'obd', 'waitress'],
  entry_points={
    'console_scripts': [
      'raspilink-server=raspberrylink_server:run_server'
    ]
  },
)
