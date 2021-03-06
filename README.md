# raspberry-link ![PyPI - Downloads](https://img.shields.io/pypi/dm/raspberrylink?style=flat-square&label=downloads%20-%20PyPi) ![GitHub release (latest by date)](https://img.shields.io/github/downloads/alejzeis/raspberry-link/latest/total?style=flat-square&label=downloads%20-%20GitHub) ![PyPI - License](https://img.shields.io/pypi/l/raspberrylink?style=flat-square)
A handsfree audio program for use with a Raspberry Pi in a car to add bluetooth audio to a "legacy" stereo.
Allows connecting a phone to a raspberry pi, which will then output audio to the 3.5mm jack or a USB sound card.
Supports control over a REST API.


For installation information visit the [wiki page](https://github.com/alejzeis/raspberry-link/wiki/Installation) as there are additional steps other than just installing the .deb file or installing from PyPi

### Features
- Bluetooth Audio Support (Add handsfree support to an old car with only an AUX IN port)
  - A2DP profile audio
  - HFP (Hands-free-profile) support, recieve and make calls over the car speakers using Ofono (microphone required)
- Media/Call controls, track information and device information available real-time over a REST API

### Some Notices:
- Bluetooth not auto-connecting, devices not able to connect, etc:
  - If you're using the Raspberry Pi 3 or Zero W they have some problems using the on-board bluetooth module. I've still not figured out entirely what is going wrong, but using a USB bluetooth dongle solves these issues. I believe the Pi 4 is fine, but I haven't tested it.
- Bluetooth Audio Support is spotty when using built-in wifi
  - The Raspberry Pi 3 variants and Zero W suffer from issues while using both the integrated wifi and bluetooth at the same time. A workaround is to use a separate wifi or bluetooth dongle instead. That is recommended for this project.
- Bluealsa needs to be compiled and installed from source, as it needs to be compiled with options to enable ofono and AAC. This is detailed on the wiki page.
