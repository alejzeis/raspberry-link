from configparser import ConfigParser
from os import getenv
from os.path import exists

default_config = """
[server]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the WSGI HTTP server to bind to
port=9098

[camera]
; Enable support for a camera connected on the network (or locally)
enabled=yes

; Address and port of the Agent on the network with the camera connected
address=192.168.1.2
port=9099


[audio]
; Enable Bluetooth audio support
; This only enables Media playback support. To enable calls and handsfree support look below
enabled=yes 
; Enable HFP (Handsfree-profile) Bluetooth support
; This allows calls to be placed and recieved over the bluetooth connection
; NOTICE: BlueALSA MUST be compiled with the --enable-ofono option, and Ofono must be installed and running
handsfree-enabled=no

[obd]
; Enable OBD (On-board diagnostics support)
enabled=no
"""


def load_config():
    config_file = getenv("RASPBERRYLINK_CONFIG")
    if config_file is None:
        config_file = "/etc/raspberrylink-server.conf"

    if not exists(config_file):
        f = open(config_file, 'w')
        f.writelines(default_config)
        f.close()

    config = ConfigParser()
    config.read(config_file)

    return config
