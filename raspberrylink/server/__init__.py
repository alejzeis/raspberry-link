from flask import Flask

from raspberrylink.server import config, obd
software_name = "RaspberryLink-Server"
software_version = "1.0.0-pre"

server_config = None
obdmanager = None
app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve
    # app.run()
    global server_config, obdmanager

    server_config = config.load_config()
    obdmanager = obd.OBDManager()

    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
