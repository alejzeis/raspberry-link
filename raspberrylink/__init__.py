from flask import Flask

software_name = "Raspberry-link"
software_version = "1.0.0"
api_version = 1

from raspberrylink import obd

obdmanager = obd.OBDManager()
app = Flask(__name__)

from raspberrylink import routes
