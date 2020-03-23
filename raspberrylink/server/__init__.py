from flask import Flask

from raspberrylink.audio import handsfree
from raspberrylink.server import config, obd
software_name = "RaspberryLink-Server"
software_version = "1.0.0-pre"

obdmanager = None
handsfree_manager = None
server_config = config.load_config()

if server_config['audio'].getboolean("enabled") and server_config['audio'].getboolean("handsfree-enabled"):
    handsfree_manager = handsfree.HandsfreeManager()

if server_config['obd'].getboolean("enabled"):
    obdmanager = obd.OBDManager()

app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve
    # app.run()
    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
