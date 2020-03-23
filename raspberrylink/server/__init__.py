from flask import Flask

from raspberrylink.server import config, obd
software_name = "RaspberryLink-Server"
software_version = "1.0.0-pre"

server_config = None
obdmanager = None
handsfree_manager = None
app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve

    from raspberrylink.audio import handsfree
    # app.run()
    global server_config, obdmanager, handsfree_manager

    server_config = config.load_config()

    if server_config['audio'].getboolean("enabled") and server_config['audio'].getboolean("handsfree-enabled"):
        handsfree_manager = handsfree.HandsfreeManager()

    if server_config['obd'].getboolean("enabled"):
        obdmanager = obd.OBDManager()

    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
