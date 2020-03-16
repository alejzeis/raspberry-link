#!/usr/bin/python

from setuptools import setup
__author__ = "jython234"

setup(
  name='raspberrylink-server',
  version='1.0.0-pre',
  description='Raspberrylink WSGI Information Server',
  author=__author__,
  author_email='jython234@gmail.com',
  license='MPL-2.0',
  url='https://github.com/jython234/raspberry-link',
  packages=['raspberrylink'],
  install_requires=['flask', 'obd', 'waitress'],
  entry_points={
    'console_scripts': [
      'raspilink-server=raspberrylink:run_server',
    ]
  },
)
