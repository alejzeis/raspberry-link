from subprocess import run, PIPE
import re

import logging

logger = logging.getLogger("RL-Util")


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
