from flask import Flask
from logging import getLogger, INFO

from raspberrylink import config

software_name = "RaspberryLink-Server"
software_version = "2.0-git"

logger = getLogger("RL-Server-Main")
logger.setLevel(INFO)

logger.info("Starting " + software_name + " " + software_version)

server_config = config.load_server_config()

app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve
    host, port = server_config['server']['interface'], server_config['server']['port']

    logger.info("Starting WSGI server on " + host + ":" + port)

    serve(app, host=host, port=int(port))
