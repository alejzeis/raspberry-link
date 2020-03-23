from subprocess import run, PIPE


def check_audio_running():
    # Check to see if the raspberrylink-audio service has ran (or if it even exists)
    # A != 0 exit code implies something is wrong or the service doesn't exist, thus no bluetooth audio support for us
    return run("systemctl status raspberrylink-audio", stdout=PIPE, stderr=PIPE, shell=True).returncode == 0


def get_current_audio_info():
    con_cmd = run("hcitool con", stdout=PIPE, stderr=PIPE, shell=True)
    if con_cmd.returncode != 0:
        print("Non-zero return code from \"hcitool con\"")
        return False, 0, "Error obtaining Information"

    output = con_cmd.stdout.decode("UTF-8")
    if len(output.split("\n")) > 2:
        bluetooth_id = output.split("\n")[1].split("ACL")[1].split("handle")[0].strip()
        info_cmd = run("hcitool info " + bluetooth_id + " | grep \"Device Name\"", stdout=PIPE, stderr=PIPE, shell=True)

        if info_cmd.returncode != 0:
            print("Non-zero return code from \"hcitool info\"")
            return True, "Error obtaining Information"

        bluetooth_name = info_cmd.stdout.decode("UTF-8").split(" ")[2]
        return True, bluetooth_name
    else:
        return False, "No Device Connected"
