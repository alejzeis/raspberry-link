from flask import Flask
from raspberrylink import config

software_name = "Raspberry-link"
software_version = "1.0.0-pre"
api_version = 1

from raspberrylink import obd

server_config = config.load_config()
obdmanager = obd.OBDManager()
app = Flask(__name__)

from raspberrylink import routes


def run_server():
    from waitress import serve
    # app.run()
    print(server_config)
    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
