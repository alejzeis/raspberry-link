from subprocess import run, PIPE
from raspberrylink.server import logger
import re


def check_audio_running():
    # Check to see if the raspberrylink-audio service has ran (or if it even exists)
    # A != 0 exit code implies something is wrong or the service doesn't exist, thus no bluetooth audio support for us
    return run("systemctl status raspberrylink-audio", stdout=PIPE, stderr=PIPE, shell=True).returncode == 0


def get_current_audio_info():
    con_cmd = run("hcitool con", stdout=PIPE, stderr=PIPE, shell=True)
    if con_cmd.returncode != 0:
        logger.error("Non-zero return code from \"hcitool con\"")
        return False, 0, "Error obtaining Information"

    output = con_cmd.stdout.decode("UTF-8")
    if output.strip() == "Connections:":
        return False, 0, "No Device Connected"
    else:
        #bluetooth_id = output.split("\n")[1].split("ACL")[1].split("handle")[0].strip()
        bluetooth_id = re.search("((?:[A-F0-9]{2}\\:){5}\\S{2})", output).group(0)
        lq_cmd = run("hcitool lq " + bluetooth_id, stdout=PIPE, stderr=PIPE, shell=True)
        if lq_cmd.returncode != 0:
            logger.error("Non-zero return code from \"hcitool lq\"")
            return False, 0, "Error obtaining Information"

        lq = int(lq_cmd.stdout.decode("UTF-8").split(" ")[2].strip())
        info_cmd = run("hcitool info " + bluetooth_id + " | grep \"Device Name\"", stdout=PIPE, stderr=PIPE, shell=True)

        if info_cmd.returncode != 0:
            logger.error("Non-zero return code from \"hcitool info\"")
            return True, lq, "Error obtaining Information"

        #bluetooth_name = info_cmd.stdout.decode("UTF-8").split(" ")[2]
        bluetooth_name = re.search("Device Name: (.*)", info_cmd.stdout.decode("UTF-8"))
        return True, lq, bluetooth_name
