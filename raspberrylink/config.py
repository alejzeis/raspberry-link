from configparser import ConfigParser
from os import getenv
from os.path import exists

default_server_config = """
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
; Name of the Raspberry Pi that will show up when other devices discover and pair to the Pi
bt-name=RaspberryLink
; Percentage from 1-100 (don't include percent sign) to set the output volume of the Pi to.
output-volume=75

[obd]
; Enable OBD (On-board diagnostics support)
enabled=no
"""

default_agent_config = """
[agent]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the Agent to listen for commands on
port=9099

; Type of camera this agent has:
; Must be either, rear, front, side, other
type=rear
"""


def load_server_config():
    config_file = getenv("RASPILINK_CONFIG")
    if config_file is None:
        config_file = "/etc/raspberrylink-server.conf"

    if not exists(config_file):
        f = open(config_file, 'w')
        f.writelines(default_server_config)
        f.close()

    config = ConfigParser()
    config.read(config_file)

    return config


def load_agent_config():
    config_location = getenv("RASPILINK_AGENT_CONFIG", "/etc/raspberrylink-agent.conf")

    if not exists(config_location):
        f = open(config_location, 'w')
        f.writelines(default_agent_config)
        f.close()

    config = ConfigParser()
    config.read(config_location)
    return config