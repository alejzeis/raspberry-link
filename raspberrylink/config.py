from configparser import ConfigParser
from os import getenv
from os.path import exists

default_config = """
[server]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the WSGI HTTP server to bind to
port=8080

[camera]
; Is there a camera connected on the network? (yes/no)
enabled=no
; IP Address of the device streaming the camera feed via GStreamer
address=127.0.0.1
; Port of the device streaming the camera feed via GStreamer
port=8088
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
