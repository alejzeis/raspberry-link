#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink',
  version='1.0.0-pre',
  description='Raspberrylink Smart-car system for Raspberry Pi',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=['raspberrylink', 'raspberrylink.server'],
  install_requires=['flask', 'obd', 'waitress'],
  entry_points={
    'console_scripts': [
      'raspilink-server=raspberrylink.server:run_server',
      'raspilink-agent=raspberrylink.agent:run_agent'
    ]
  },
)
