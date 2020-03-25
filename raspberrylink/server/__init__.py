from flask import Flask

from raspberrylink.server import config, obd, communicator
software_name = "RaspberryLink-Server"
software_version = "1.0.0-pre"

obdmanager = None
audio_comm = None
server_config = config.load_config()

if server_config['audio'].getboolean("enabled"):
    audio_comm = communicator.AudioServiceCommunicator()

if server_config['obd'].getboolean("enabled"):
    obdmanager = obd.OBDManager()

app = Flask(__name__)

from raspberrylink.server import routes


def run_server():
    from waitress import serve
    serve(app, host=server_config['server']['interface'], port=int(server_config['server']['port']))
