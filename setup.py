#!/usr/bin/python

from setuptools import setup

__author__ = "alejzeis"

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='raspberrylink',
    version='2.2.1+git',
    description='Handsfree bluetooth audio server for use in a car on a Raspberry Pi',
    author=__author__,
    author_email='alejzeis@pm.me',
    license='MPL-2.0',
    url='https://github.com/alejzeis/raspberry-link',
    packages=['raspberrylink', 'raspberrylink.audio'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['flask', 'waitress', 'dbus-python', 'PyGObject'],
    entry_points={
        'console_scripts': [
            'raspilink-server=raspberrylink.server:startup',
            'raspilink-agent=raspberrylink.agent:run_agent'
        ]
    },
    python_requires=">=3.6",
    data_files=[
        ('/opt/raspberrylink/service-files', ['init-scripts/raspberrylink-agent.service',
                                              'init-scripts/raspberrylink.service', 'init-scripts/raspberrylink',
                                              'init-scripts/raspberrylink-diskless-init'],
         ),
        ('/opt/raspberrylink', ['bluetooth-scripts/raspilink-bt-init', 'bluetooth-scripts/raspilink-bt-agent.py']),
        ('/etc/', ['default-config/raspberrylink-server.conf'])
    ]
)
