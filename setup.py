#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink',
  version='1.0-git',
  description='Raspberrylink Smart-car system for Raspberry Pi',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=['raspberrylink', 'raspberrylink.server', 'raspberrylink.audio'],
  install_requires=['flask', 'obd', 'waitress', 'dbus-python', 'PyGObject'],
  entry_points={
    'console_scripts': [
      'raspilink-server=raspberrylink.server:run_server',
      'raspilink-agent=raspberrylink.agent:run_agent',
      'raspilink-audio=raspberrylink.audio.core:bootstrap'
    ]
  },
  data_files=[
    ('/usr/lib/systemd/system/', ['raspberrylink-agent.service', 'raspberrylink-audio.service',
                                  'raspberrylink-server.service'],
     ),
    ('/usr/src/raspberrylink', ['bt-audio/raspilink-audio-start', 'bt-audio/raspilink-bt-agent.py'])
  ]
)
