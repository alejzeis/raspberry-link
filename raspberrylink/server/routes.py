from flask import jsonify, request
from raspberrylink.server import app, software_name, software_version, server_config, audio_manager

api_version_major = 5
api_version_minor = 1


@app.route('/apiver')
def apiver():
    return jsonify({
        "major": api_version_major,
        "minor": api_version_minor
    })


@app.route('/feature_request')
def feature_request():
    obj = {
        "server": software_name,
        "version": software_version,
        "audio": server_config['audio'].getboolean("enabled")
    }
    return jsonify(obj)


@app.route('/checkin')
def checkin():
    audio_support = server_config['audio'].getboolean("enabled")
    res_obj = {}

    if audio_support:
        res_obj["device"] = audio_manager.connected_device
        res_obj["media"] = audio_manager.handsfree_mgr.track_info
        res_obj["calls"] = audio_manager.handsfree_mgr.calls

    return jsonify(res_obj)


@app.route('/calls/answer')
def answer_call():
    if not server_config['audio'].getboolean("enabled"):
        return "Audio Service is offline", 500

    path = request.args.get("path", None)
    if path is None:
        return "Required argument \"path\" missing", 400

    if audio_manager.handsfree_mgr.answer_call(path):
        return "", 204
    else:
        return "Failed to answer call", 500


@app.route('/calls/hangup')
def hangup_call():
    if not server_config['audio'].getboolean("enabled"):
        return "Audio Service is offline", 500

    path = request.args.get("path", None)
    if path is None:
        return "Required argument \"path\" missing", 400

    if audio_manager.handsfree_mgr.hangup_call(path):
        return "", 204
    else:
        return "Failed to hangup call", 500


@app.route('/media/play')
def music_play():
    if not server_config['audio'].getboolean("enabled"):
        return "Audio Service is offline", 500

    audio_manager.handsfree_mgr.music_pause()
    return "", 204


@app.route('/media/pause')
def music_pause():
    if not server_config['audio'].getboolean("enabled"):
        return "Audio Service is offline", 500

    audio_manager.handsfree_mgr.music_pause()
    return "", 204
