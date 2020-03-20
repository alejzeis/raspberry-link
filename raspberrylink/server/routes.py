from flask import jsonify
from raspberrylink.server import app, software_name, software_version, server_config
from raspberrylink.server import util

api_version_major = 3
api_version_minor = 1


@app.route('/apiver')
def apiver():
    return jsonify({
        "major": api_version_major,
        "minor": api_version_minor
    })


@app.route('/feature_request')
def feature_request():
    audio_running = util.check_audio_running()
    obj = {
        "vehicle": "Unknown",  # TODO: Vehicle information detection
        "server": software_name,
        "version": software_version,
        "audio": audio_running and server_config['audio'].getboolean("enabled"),
        "handsfree": audio_running and server_config['audio'].getboolean("handsfree-enabled"),
        "camera": server_config['camera'].getboolean("enabled"),
        "cameraAddress": server_config['camera']['address'],
        "cameraPort": int(server_config['camera']['port']),
        "obd": server_config['obd'].getboolean("enabled")
    }
    return jsonify(obj)


@app.route('/checkin')
def checkin():
    obd_support = server_config['obd'].getboolena("enabled")
    audio_support = util.check_audio_running() and server_config['audio'].getboolean("enabled")
    res_obj = {
        "coolant": 0,
        "oil": 0,
        "mpg": 0,
        "distance_mil": 0,
        "current_dtc": 0,
        "dtc": {},
        "load": 0,
        "audio": {
            "connected": False,
            "signal": 0,
            "name": "Unknown"
        }
    }

    if obd_support:
        # TODO: OBD Information
        pass

    if audio_support:
        stats = util.get_current_audio_info()
        res_obj['audio']['connected'], res_obj['audio']['signal'], res_obj['audio']['name'] = stats

    return res_obj