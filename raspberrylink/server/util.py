from subprocess import run, PIPE


def check_audio_running():
    # Check to see if the raspberrylink-audio service has ran (or if it even exists)
    # A != 0 exit code implies something is wrong or the service doesn't exist, thus no bluetooth audio support for us
    return run("systemctl status raspberrylink-audio", stdout=PIPE, stderr=PIPE, shell=True).returncode == 0
