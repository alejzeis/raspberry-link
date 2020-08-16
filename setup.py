#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink',
  version='2.0-git',
  description='Raspberrylink Smart-car system for Raspberry Pi',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=['raspberrylink', 'raspberrylink.server', 'raspberrylink.audio'],
  install_requires=['flask', 'waitress', 'dbus-python', 'PyGObject'],
  entry_points={
    'console_scripts': [
      'raspilink-server=raspberrylink.server:run_server',
      'raspilink-audio=raspberrylink.audio.core:bootstrap'
    ]
  },
  data_files=[
    ('/usr/lib/systemd/system/', ['raspberrylink-audio.service',
                                  'raspberrylink-server.service'],
     ),
    ('/usr/src/raspberrylink', ['bt-audio/raspilink-audio-start', 'bt-audio/raspilink-bt-agent.py'])
  ]
)
