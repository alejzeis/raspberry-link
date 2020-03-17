from flask import jsonify, request
from raspberrylink_server import app, software_name, software_version, server_config
from raspberrylink_server import util

api_version_major = 2
api_version_minor = 1

agents = {}


@app.route('/apiver')
def apiver():
    return jsonify({
        "major": api_version_major,
        "minor": api_version_minor
    })


@app.route('/register_agent')
def register_agent():
    if request.args.get('id') is None:
        return "Parameter \"id\" required.", 400
    elif request.args.get('type') is None:
        return "Parameter \"type\" required", 400

    if request.args.get('id') in agents:
        return "Agent already registered.", 409

    # TODO: Periodically ping Agents to check their state and update in dict
    agents[request.args.get('id')] = {
        "ip": request.remote_addr,
        "type": request.args.get('type')
    }

    return "", 204


@app.route('/feature_request')
def feature_request():
    audio_running = util.check_audio_running()
    obj = {
        "vehicle": "Unknown",
        "server": software_name,
        "version": software_version,
        "audio": audio_running and server_config['audio'].getboolean("enabled"),
        "handsfree": audio_running and server_config['audio'].getboolean("handsfree-enabled"),
        "camera": server_config['camera'].getboolean("enabled"),
        "obd": server_config['obd'].getboolean("enabled")
    }
    return jsonify(obj)
