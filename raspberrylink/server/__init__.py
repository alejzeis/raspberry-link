from flask import Flask
from logging import getLogger, INFO

from raspberrylink.server import obd, communicator
from raspberrylink import config

software_name = "RaspberryLink-Server"
software_version = "1.0a1"

logger = getLogger("RL-Server-Main")
logger.setLevel(INFO)

logger.info("Starting " + software_name + " " + software_version)

obdmanager = None
audio_comm = None
server_config = config.load_server_config()

if server_config['audio'].getboolean("enabled"):
    audio_comm = communicator.AudioServiceCommunicator()

if server_config['obd'].getboolean("enabled"):
    obdmanager = obd.OBDManager()

app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve
    host, port = server_config['server']['interface'], server_config['server']['port']

    logger.info("Starting WSGI server on " + host + ":" + port)

    serve(app, host=host, port=int(port))
