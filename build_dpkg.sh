#!/bin/sh

rm -rf dist

chmod +x bt-audio/raspilink-audio-start
chmod +x bt-audio/raspilink-audio-udev-hook

python3 setup.py --command-packages=stdeb.command bdist_deb