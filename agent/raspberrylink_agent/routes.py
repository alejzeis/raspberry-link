from raspberrylink_agent import app

supported_api_version_major = 2
supported_api_version_minor = 1


@app.route('/stream/start')
def apiver():
    # TODO: Start GStreamer Stream
    return "", 501


@app.route('/stream/stop')
def stop_stream():
    # TODO: Stop GStreamer Stream
    return "", 501
