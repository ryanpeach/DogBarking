import pyaudio
import numpy as np

# REF: https://gist.github.com/mabdrabo/8678538
FORMAT = pyaudio.paFloat32


class Recorder:
    def __init__(self, audio, frames_per_buffer, form, channels, sample_freq):
        self.audio = audio
        self.device_index = self.find_input_device()
        self.frames_per_buffer = frames_per_buffer
        self.channels = channels
        self.sample_freq = sample_freq
        self.format = form

    def start(self):
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_freq,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.frames_per_buffer,
        )

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def find_input_device(self) -> int:
        device_index = None
        for i in range(self.audio.get_device_count()):
            devinfo = self.audio.get_device_info_by_index(i)
            print("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    print("Found an input: device %d - %s" % (i, devinfo["name"]))
                    device_index = i
                    return device_index

        if device_index is None:
            print("No preferred input found; using default input device.")

        return device_index

    def __next__(self) -> np.ndarray:
        """REF: https://stackoverflow.com/questions/19629496/get-an-audio-sample-as-float-number-from-pyaudio-stream # noqa"""
        import numpy

        stream = self.stream.open(
            format=FORMAT,
            channels=self.channels,
            rate=self.sample_freq,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
        )
        data = stream.read(self.frames_per_buffer * self.sample_freq)
        decoded = numpy.fromstring(data, "Float32")
        return decoded


class Player:
    def __init__(self, audio, volume, duration, freq, fs, form):
        self.audio = audio
        self.duration = duration
        self.freq = freq
        self.fs = fs
        self.volume = volume
        self.format = form

    def start(self):
        # for paFloat32 sample values must be in range [-1.0, 1.0]
        self.stream = self.audio.open(
            format=self.format, channels=1, rate=self.fs, output=True
        )

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def play_sound(self):
        """REF: https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python"""
        # generate samples, note conversion to float32 array
        samples = (
            np.sin(2 * np.pi * np.arange(self.fs * self.duration) * self.freq / self.fs)
        ).astype(np.float32)

        # play. May repeat with different volume values (if done interactively)
        self.stream.write(self.volume * samples)
