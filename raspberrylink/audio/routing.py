from subprocess import Popen, PIPE


class AudioRouter:
    audio_manager = None

    def __init__(self, audio_manager):
        self.audio_manager = audio_manager

    def on_start_media_playback(self):
        pass

    def on_stop_media_playback(self):
        pass

    def on_start_call(self):
        pass

    def on_end_call(self):
        pass


class PhysicalAudioRouter(AudioRouter):
    aplay_a2dp = None
    aplay_sco = None
    aplay_mic = None
    arec_mic = None

    bluealsa_aplay_exec = None
    aplay_exec = None
    arecord_exec = None

    def __init__(self, audio_manager):
        super().__init__(audio_manager)

        self.bluealsa_aplay_exec = audio_manager.config['audio']['bluealsa-aplay-exec']
        self.aplay_exec = audio_manager.config['audio']['aplay-exec']
        self.arecord_exec = audio_manager.config['audio']['arecord-exec']

    def on_start_media_playback(self):
        if self.aplay_a2dp is None:
            self.aplay_a2dp = Popen([self.bluealsa_aplay_exec,
                                    "--pcm-buffer-time=1000000", "00:00:00:00:00:00", "--profile-a2dp"],
                                    stdout=PIPE, stderr=PIPE, shell=False)

    def on_stop_media_playback(self):
        if self.aplay_a2dp is not None:
            self.aplay_a2dp.terminate()
            self.aplay_a2dp.wait()

            self.aplay_a2dp = None

    def on_start_call(self):
        if self.aplay_sco is None:
            self.aplay_sco = Popen([self.bluealsa_aplay_exec, "--profile-sco"],
                                   stdout=PIPE, stderr=PIPE, shell=False)

        # Terminate aplay and arecord if already running
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()

            self.aplay_mic = None
        if self.arec_mic is not None:
            self.arec_mic.terminate()
            self.arec_mic.wait()

            self.arec_mic = None

        device_id = self.audio_manager.connected_device['address']
        # Pipe Arecord output to Aplay to send over the SCO link
        self.arec_mic = Popen([self.arecord_exec, "-D", self.audio_manager.config['audio']['arecord-device'],
                               "-f", self.audio_manager.config['audio']['arecord-format'],
                               "-c", self.audio_manager.config['audio']['arecord-channels'],
                               "-r", self.audio_manager.config['audio']['arecord-sample-rate'], "-"],
                              stdout=PIPE, shell=False)
        self.aplay_mic = Popen([self.aplay_exec, "-D",
                                "bluealsa:SRV=org.bluealsa,DEV=" + device_id + ",PROFILE=sco", "-"],
                               stdout=PIPE, stdin=self.arec_mic.stdout, shell=False)

    def on_end_call(self):
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()

            self.aplay_mic = None

        if self.arec_mic is not None:
            self.arec_mic.terminate()
            self.arec_mic.kill()

            self.arec_mic = None

        if self.aplay_sco is not None:
            self.aplay_sco.terminate()
            self.aplay_sco.wait()

            self.aplay_sco = None
