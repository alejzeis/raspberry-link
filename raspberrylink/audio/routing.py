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

    def __init__(self, audio_manager):
        super().__init__(audio_manager)

    def on_start_media_playback(self):
        if self.aplay_a2dp is None:
            self.aplay_a2dp = Popen("bluealsa-aplay --pcm-buffer-time=1000000 00:00:00:00:00:00 --profile-a2dp",
                               stdout=PIPE, stderr=PIPE, shell=True)

    def on_stop_media_playback(self):
        if self.aplay_a2dp is not None:
            self.aplay_a2dp.terminate()
            self.aplay_a2dp.wait()

    def on_start_call(self):
        if self.aplay_sco is None:
            self.aplay_sco = Popen("bluealsa-aplay 00:00:00:00:00:00 --profile-sco", stdout=PIPE, stderr=PIPE, shell=True)

        if self.aplay_mic is None:
            # TODO: Begin microphone process
            pass

    def on_end_call(self):
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()

        if self.aplay_sco is not None:
            self.aplay_sco.terminate()
            self.aplay_sco.wait()
