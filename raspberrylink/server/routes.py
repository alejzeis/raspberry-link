from flask import jsonify, request
from raspberrylink.server import app, software_name, software_version, server_config
from raspberrylink.server import audio_comm
from raspberrylink import util

api_version_major = 4
api_version_minor = 2


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
    }
    return jsonify(obj)


@app.route('/checkin')
def checkin():
    audio_support = util.check_audio_running() and server_config['audio'].getboolean("enabled")
    res_obj = {
        "audio": {
            "connected": False,
            "signal_quality": 0,
            "name": "Unknown",
            "music": {}
        },
        "calls": {
        }
    }

    if audio_support:
        stats = util.get_current_audio_info()
        res_obj['audio']['connected'], res_obj['audio']['signal_quality'], res_obj['audio']['name'] = stats[slice(3)]

    if audio_support and server_config['audio'].getboolean("handsfree-enabled"):
        res_obj['calls'] = audio_comm.active_calls
        res_obj['music'] = audio_comm.track_data

    return jsonify(res_obj)


@app.route('/calls/answer')
def answer_call():
    if not (util.check_audio_running() and server_config['audio'].getboolean("handsfree-enabled")):
        return "Handsfree support not enabled or Audio Service is offline", 500

    path = request.args.get("path", None)
    if path is None:
        return "Required argument \"path\" missing", 400

    if audio_comm.answer_call(path):
        return "", 204
    else:
        return "Failed to answer call", 500


@app.route('/calls/hangup')
def hangup_call():
    if not (util.check_audio_running() and server_config['audio'].getboolean("handsfree-enabled")):
        return "Handsfree support not enabled or Audio Service is offline", 500

    path = request.args.get("path", None)
    if path is None:
        return "Required argument \"path\" missing", 400

    if audio_comm.hangup_call(path):
        return "", 204
    else:
        return "Failed to hangup call", 500


@app.route('/media/play')
def music_play():
    if not util.check_audio_running():
        return "Audio Service is offline", 500

    audio_comm.music_play()
    return "", 204


@app.route('/media/pause')
def music_pause():
    if not util.check_audio_running():
        return "Audio Service is offline", 500

    audio_comm.music_pause()
    return "", 204
