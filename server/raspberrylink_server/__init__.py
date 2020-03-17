from flask import Flask
from raspberrylink_server import obd
from raspberrylink_server import config

software_name = "RaspberryLink-Server"
software_version = "1.0.0-pre"

server_config = config.load_config()
obdmanager = obd.OBDManager()
app = Flask(__name__)

from raspberrylink_server import routes


def run_server():
    from waitress import serve
    # app.run()
    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
