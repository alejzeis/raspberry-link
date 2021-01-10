from configparser import ConfigParser
from os import getenv
from os.path import exists

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
        raise FileNotFoundError("Config file: " + config_file + " doesn't exist!")

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
