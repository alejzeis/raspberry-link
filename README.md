# raspberry-link
"Smart car" server solution for a raspberry pi, handles bluetooth audio and OBD information

### Features
- Bluetooth Audio Support (Add handsfree support to an old car with only an AUX IN port)
  - A2DP profile audio
  - HFP (Hands-free-profile) support, recieve and make calls over the car speakers using Ofono (USB microphone required)
- Rear-view Camera
  - Connect a camera locally or to another device on a network and stream to the user interface
- OBD (On board diagnostics)
  - View information about temperatures, check engine light, and more

### Notices:
- Bluetooth Audio Support is spotty when using built-in wifi
  - The Raspberry Pi 3 variants and Zero W suffer from issues while using both the integrated wifi and bluetooth at the same time. A workaround is to use a separate wifi or bluetooth dongle instead. That is recommended for this project.
- If activating Handsfree-call support, then Ofono is required. Bluealsa must **NOT** be installed from the Raspbian package manager, it must be compiled from source with the ``--enable-ofono`` option