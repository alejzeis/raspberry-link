from flask import Flask

software_name = "RaspberryLink-Agent"
software_version = "1.0.0-pre"

app = Flask(__name__)

from raspberrylink_agent import routes


def run_agent():
    from waitress import serve
    from os import getenv

    # TODO: Register agent with Server

    serve(app, port=int(getenv("AGENT_PORT", 9099)))
