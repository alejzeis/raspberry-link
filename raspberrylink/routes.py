from flask import jsonify
from raspberrylink import app, software_name, software_version, api_version, obdmanager, server_config, util


@app.route('/info/apiver')
def apiver():
    return str(api_version)


@app.route('/info/static')
def info_static():
    obj = {
        "vehicle": "",
        "server": software_name,
        "version": software_version,
        "audio": util.check_audio_support(),
        "camera": server_config['camera'].getboolean("enabled"),
        "steamIP": server_config['camera']['address'],
        "streamPort": server_config['camera']['port']

    }
    return jsonify(obj)
