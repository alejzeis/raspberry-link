#!/usr/bin/python

from setuptools import setup

__author__ = "jython234"

setup(
    name='raspberrylink',
    version='2.0-git',
    description='Raspberry Pi based handsfree audio server for automotive settings',
    author=__author__,
    author_email='jython234@gmail.com',
    license='MPL-2.0',
    url='https://github.com/jython234/raspberry-link',
    packages=['raspberrylink', 'raspberrylink.audio'],
    install_requires=['flask', 'waitress', 'dbus-python', 'PyGObject'],
    entry_points={
        'console_scripts': [
            'raspilink-server=raspberrylink.server:startup',
            'raspilink-agent=raspberrylink.agent:run_agent'
        ]
    },
    data_files=[
        ('/opt/raspberrylink', ['raspberrylink-agent.service', 'raspberrylink.service'],
         ),
        ('/opt/raspberrylink', ['bluetooth-scripts/raspilink-bt-init', 'bluetooth-scripts/raspilink-bt-reconnect',
                                'bluetooth-scripts/raspilink-bt-agent.py'])
    ]
)
