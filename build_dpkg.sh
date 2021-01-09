#!/bin/sh

rm -rf dist
rm -rf deb_dist

chmod +x bluetooth-scripts/raspilink-bt-agent.py
chmod +x bluetooth-scripts/raspilink-bt-init

DEB_BUILD_OPTIONS=nocheck python3 setup.py --command-packages=stdeb.command bdist_deb
