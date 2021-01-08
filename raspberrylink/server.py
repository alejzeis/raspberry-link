from flask import Flask, jsonify, request
from logging import getLogger, INFO

import threading
from waitress import serve

from raspberrylink import config
from raspberrylink.audio import core as audio_core

software_name = "RaspberryLink-Server"
software_version = "2.0-git"
api_version_major = 5
api_version_minor = 1


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

    def waitress_serve():
        logger.info("Starting WSGI server on " + host + ":" + port)

        serve(app, host=host, port=int(port))

    threading.Thread(target=waitress_serve, daemon=True).start()


def startup():
    import dbus
    from gi.repository import GLib

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger = getLogger("RL-Server-Main")
    logger.setLevel(INFO)
    logger.info("Starting " + software_name + " " + software_version)

    server_config = config.load_server_config()
    run_server(logger, audio_core.bootstrap(server_config), server_config)

    mainloop = GLib.MainLoop()
    mainloop.run()
