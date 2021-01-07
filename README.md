# raspberry-link
A handsfree audio program for use with a Raspberry Pi in a car to add bluetooth audio to a "legacy" stereo.

For installation information visit the [wiki](https://github.com/jython234/raspberry-link/wiki/Installation)

### Dependencies
For all features:
```
gstreamer1.0 gstreamer1.0-rtsp gstreamer1.0-plugins-bad
python3 python3-pip libcairo2-dev libgirepository1.0-dev
```

### Features
Any of these can be disabled/enabled

- Bluetooth Audio Support (Add handsfree support to an old car with only an AUX IN port)
  - A2DP profile audio
  - HFP (Hands-free-profile) support, recieve and make calls over the car speakers using Ofono (microphone required)

### Notices:
- Bluetooth Audio Support is spotty when using built-in wifi
  - The Raspberry Pi 3 variants and Zero W suffer from issues while using both the integrated wifi and bluetooth at the same time. A workaround is to use a separate wifi or bluetooth dongle instead. That is recommended for this project.
- Bluealsa needs to be compiled and installed from source, as it needs to be compiled with options to enable ofono and AAC. This is detailed on the wiki page.