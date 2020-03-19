from os import getenv
from os.path import exists
import socket, configparser, subprocess, atexit


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


def load_config():
    config_location = getenv("RASPILINK_AGENT_CONFIG", "/etc/raspberrylink-agent.conf")
    print("Loading configuration from " + config_location)

    if not exists(config_location):
        print("Configuration not found, writing and loading default...")
        f = open(config_location)
        f.writelines(default_config)
        f.close()

    config = configparser.ConfigParser()
    config.read(config_location)
    return config


stream_process = None


def run_agent():
    print("Starting Raspberrylink Agent...")
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

        if data == "REQSTREAM":
            print("Received Start Stream Request from " + str(address))
            if stream_process is not None:
                pass
            else:
                # Send back to the address we got the packet from
                gstreamer_command[15] = ("host=" + address[0])
                stream_process = subprocess.Popen(gstreamer_command)
                print("Started GStreamer Process")
        elif data == "STOPSTREAM":
            print("Received Stop Stream Request from " + str(address))
            if not stream_process:
                pass
            else:
                stream_process.terminate()
                print("Terminated GStreamer Process with exit code: " + str(stream_process.poll()))
                stream_process = None
        else:
            print("Unknown message from " + str(address))
