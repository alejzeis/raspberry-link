from flask import Flask
from logging import getLogger, INFO

from raspberrylink import config

software_name = "RaspberryLink-Server"
software_version = "2.0-git"

logger = getLogger("RL-Server-Main")
logger.setLevel(INFO)

server_config = config.load_server_config()
audio_manager = None

app = Flask(__name__)

from raspberrylink.server import routes


# This needs to be called after startup()
def run_server():
    from waitress import serve
    from time import sleep
    host, port = server_config['server']['interface'], server_config['server']['port']

    sleep(2)
    audio_manager.attempt_reconnect(server_config)

    logger.info("Starting WSGI server on " + host + ":" + port)

    serve(app, host=host, port=int(port))


def startup():
    global audio_manager

    import threading
    import dbus
    from gi.repository import GLib
    from raspberrylink.audio import core as audio_core

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    logger.info("Starting " + software_name + " " + software_version)

    audio_manager = audio_core.bootstrap(server_config)

    threading.Thread(target=run_server, daemon=True).start()

    mainloop = GLib.MainLoop()
    mainloop.run()
