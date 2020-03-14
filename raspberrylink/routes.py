from flask import jsonify
from raspberrylink import app, software_name, software_version, api_version, obdmanager


@app.route('/info/apiver')
def apiver():
    return str(api_version)


@app.route('/info/static')
def info_static():
    obj = {
        "vehicle": "",
        "server": software_name,
        "version": software_version,
        "audio": False,
        "camera": False,
        "steamIP": "127.0.0.1",
        "streamPort": 9999

    }
    return jsonify(obj)
