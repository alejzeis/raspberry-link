from os import getenv
from os.path import exists
import socket
import configparser
import subprocess
import logging
import atexit


default_config = """
[agent]
; Interface for the WSGI HTTP server to bind on
interface=0.0.0.0
; Port for the Agent to listen for commands on
port=9099

; Type of camera this agent has:
; Must be either, rear, front, side, other
type=rear
"""
gstreamer_command = ['gst-launch-1.0', '-e', 'v4l2src', 'do-timestamp=true', '!',
                     'video/x-h264,width=640,height=480,framerate=30/1', '!',
                     'h264parse', '!', 'rtph264pay', 'config-interval=1', '!',
                     'gdppay', '!', 'udpsink', 'host=192.168.1.3', 'port=9097']

logger = logging.getLogger("RL-Agent")
logger.setLevel(logging.INFO)


def load_config():
    config_location = getenv("RASPILINK_AGENT_CONFIG", "/etc/raspberrylink-agent.conf")
    logger.info("Loading configuration from " + config_location)

    if not exists(config_location):
        logger.warning("Configuration not found, writing and loading default...")
        f = open(config_location, 'w')
        f.writelines(default_config)
        f.close()

    config = configparser.ConfigParser()
    config.read(config_location)
    return config


stream_process = None


def run_agent():
    logger.info("Starting Raspberrylink Agent...")
    config = load_config()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config['agent']['interface'], int(config['agent']['port'])))

    global stream_process

    def exit_handler():
        if stream_process is not None:
            stream_process.terminate()
            stream_process.poll()

    atexit.register(exit_handler)

    while True:
        data, address = sock.recvfrom(1024)

        if data.decode("UTF-8") == "REQSTREAM":
            logger.info("Received Start Stream Request from " + str(address))
            if stream_process is not None:
                pass
            else:
                # Send back to the address we got the packet from
                gstreamer_command[15] = ("host=" + address[0])
                stream_process = subprocess.Popen(gstreamer_command)
                logger.debug("Started GStreamer Process")
        elif data.decode("UTF-8") == "STOPSTREAM":
            logger.info("Received Stop Stream Request from " + str(address))
            if not stream_process:
                pass
            else:
                stream_process.terminate()
                logger.debug("Terminated GStreamer Process with exit code: " + str(stream_process.poll()))
                stream_process = None
        else:
            logger.warning("Unknown message from " + str(address))
