from configparser import ConfigParser
from os import getenv
from os.path import exists

default_server_config = """
[server]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the WSGI HTTP server to bind to
port=9098

[audio] 
; The Bluetooth device address of the Bluetooth adapter on the Pi
; This is only used if you have multiple adapters, otherwise leave as default
bt-adapter-address=00:00:00:00:00:00

; Name of the Raspberry Pi that will show up when other devices discover and pair to the Pi
bt-name=RaspberryLink

; Percentage from 1-100 (don't include percent sign) to set the output volume of the Pi to.
output-volume=75
; Percentage from 1-100 (don't include percent sign) to set the input volume to.
input-volume=100
; Numid for the Audio Playback device (You can find this using "amixer controls", see wiki for more information)
; Usually this won't need to be changed unless you are using a USB Sound device.
; For more information on how to make sure audio goes through the onboard analog port, or using a USB Sound device, see the wiki.
mixer-numid-output=1
; Same as above except for microphone.
mixer-numid-input=0
"""


def load_server_config():
    config_file = getenv("RASPILINK_CONFIG")
    if config_file is None:
        config_file = "/etc/raspberrylink.conf"

    if not exists(config_file):
        f = open(config_file, 'w')
        f.writelines(default_server_config)
        f.close()

    config = ConfigParser()
    config.read(config_file)

    return config