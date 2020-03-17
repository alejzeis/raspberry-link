#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink_agent',
  version='1.0.0-pre',
  description='RaspberryLink Agent that runs on camera devices',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=[''],
  install_requires=['flask', 'waitress', 'requests'],
  entry_points={
    'console_scripts': [
      'raspilink-agent=raspberrylink_agent:run_agent'
    ]
  },
)
