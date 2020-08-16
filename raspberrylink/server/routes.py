from flask import jsonify, request
from raspberrylink.server import app, software_name, software_version, server_config
from raspberrylink.server import audio_comm
from raspberrylink import util

api_version_major = 4
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
        "server": software_name,
        "version": software_version,
        "audio": audio_running
    }
    return jsonify(obj)


@app.route('/checkin')
def checkin():
    audio_support = util.check_audio_running()
    res_obj = {
        "audio": {
            "connected": False,
            "signal_quality": 0,
            "name": "Unknown",
            "artist": "",
            "title": ""
        },
        "calls": {
        }
    }

    if audio_support:
        stats = util.get_current_audio_info()
        res_obj['audio']['connected'], res_obj['audio']['signal_quality'], res_obj['audio']['name'] = stats[slice(3)]
        res_obj['calls'] = audio_comm.active_calls

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


@app.route('/playback/back')
def music_back():
    pass


@app.route('/playback/play')
def music_play():
    pass


@app.route('/playback/pause')
def music_pause():
    pass


@app.route('/playback/skip')
def music_skip():
    pass
