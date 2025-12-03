from flask import Flask, jsonify, request
from logging import getLogger, INFO, DEBUG

import threading
from waitress import serve

from raspberrylink import config
from raspberrylink.audio import core as audio_core

software_name = "RaspberryLink-Server"
software_version = "2.2.1+git"
api_version_major = 5
api_version_minor = 3


# This needs to be called after startup()
def run_server(logger, audio_manager, server_config):
    host, port = server_config['server']['interface'], server_config['server']['port']

    app = Flask(__name__)

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
            "audio": server_config['audio'].getboolean("enabled"),
            "call-support": server_config['audio'].getboolean("call-support-enabled")
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
            return "Audio Service is offline", 503
        elif not server_config['audio'].getboolean("call-support-enabled"):
            return "Server does not support call-related functions", 503

        path = request.args.get("path", None)
        if path is None:
            return "Required argument \"path\" missing", 400

        try:
            if audio_manager.handsfree_mgr.answer_call(path):
                return "", 204
            else:
                return "That call wasn't found", 404
        except Exception as e:
            logger.error("Exception while answering " + path + ", " + str(e))
            return "Failed to answer call", 500

    @app.route('/calls/hangup')
    def hangup_call():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503
        elif not server_config['audio'].getboolean("call-support-enabled"):
            return "Server does not support call-related functions", 503

        path = request.args.get("path", None)
        if path is None:
            return "Required argument \"path\" missing", 400

        try:
            if audio_manager.handsfree_mgr.hangup_call(path):
                return "", 204
            else:
                return "That call wasn't found", 404
        except Exception as e:
            logger.error("Exception while hanging up on " + path + ", " + str(e))
            return "Failed to hangup call", 500

    @app.route('/calls/hangupall')
    def hangup_all_calls():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503
        elif not server_config['audio'].getboolean("call-support-enabled"):
            return "Server does not support call-related functions", 503

        try:
            audio_manager.handsfree_mgr.hangup_all()
            return "", 204
        except Exception as e:
            logger.error("Exception while hanging up on all calls, " + str(e))
            return "Failed to hangup all calls", 500

    @app.route('/calls/dial')
    def dial_call():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503
        elif not server_config['audio'].getboolean("call-support-enabled"):
            return "Server does not support call-related functions", 503

        number = request.args.get("number", None)
        if number is None:
            return "Required argument \"number\" missing", 400

        try:
            audio_manager.handsfree_mgr.dial_call(number)
            return "", 204
        except Exception as e:
            logger.error("Exception while dialing number " + number + ", " + str(e))
            return "Failed to dial number", 500

    @app.route('/media/play')
    def music_play():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503

        audio_manager.handsfree_mgr.music_play()
        return "", 204

    @app.route('/media/pause')
    def music_pause():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 500

        audio_manager.handsfree_mgr.music_pause()
        return "", 204

    @app.route('/media/skip')
    def music_skip():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503

        audio_manager.handsfree_mgr.music_skip()
        return "", 204

    @app.route('/media/back')
    def music_back():
        if not server_config['audio'].getboolean("enabled"):
            return "Audio Service is offline", 503

        audio_manager.handsfree_mgr.music_back()
        return "", 204

    def waitress_serve():
        logger.info("Starting WSGI server on " + host + ":" + port)

        serve(app, host=host, port=int(port))

    threading.Thread(target=waitress_serve, daemon=True).start()


def startup():
    import dbus
    import os
    from gi.repository import GLib

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger = getLogger("RL-Server-Main")
    if os.getenv("RASPILINK_DEBUG") == "1":
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)
    logger.info("Starting " + software_name + " " + software_version)

    server_config = config.load_server_config()
    run_server(logger, audio_core.bootstrap(server_config), server_config)

    mainloop = GLib.MainLoop()
    mainloop.run()
