#!/bin/sh

rm -rf dist
rm -rf deb_dist

chmod +x bt-audio/raspilink-audio-start

DEB_BUILD_OPTIONS=nocheck python3 setup.py --command-packages=stdeb.command bdist_deb