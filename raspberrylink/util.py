from subprocess import run, PIPE
import re

import logging

logger = logging.getLogger("RL-Util")


def check_audio_running():
    # Check to see if the raspberrylink-audio service has ran (or if it even exists)
    # A != 0 exit code implies something is wrong or the service doesn't exist, thus no bluetooth audio support for us
    return run("systemctl status raspberrylink-audio", stdout=PIPE, stderr=PIPE, shell=True).returncode == 0


def get_device_connected():
    con_cmd = run("hcitool con", stdout=PIPE, stderr=PIPE, shell=True)
    if con_cmd.returncode != 0:
        return False, ""

    output = con_cmd.stdout.decode("UTF-8")
    if output.strip() == "Connections:":
        return False, ""
    else:
        return True, re.search("((?:[A-F0-9]{2}\\:){5}\\S{2})", output).group(0)


def get_current_audio_info():
    device_connected =  get_device_connected()
    if not device_connected[0]:
        return False, 0, "No Device Connected", ""
    else:
        bluetooth_id = device_connected[1]
        lq_cmd = run("hcitool lq " + bluetooth_id, stdout=PIPE, stderr=PIPE, shell=True)
        if lq_cmd.returncode != 0:
            logger.error("Non-zero return code from \"hcitool lq\"")
            return False, 0, "Error obtaining Information", ""

        lq = int(lq_cmd.stdout.decode("UTF-8").split(" ")[2].strip())
        info_cmd = run("hcitool info " + bluetooth_id + " | grep \"Device Name\"", stdout=PIPE, stderr=PIPE, shell=True)

        if info_cmd.returncode != 0:
            logger.error("Non-zero return code from \"hcitool info\"")
            return True, lq, "Error obtaining Information", ""

        bluetooth_name = re.search("Device Name: (.*)", info_cmd.stdout.decode("UTF-8")).group(0)
        return True, lq, bluetooth_name, bluetooth_id
