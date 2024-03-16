import functools
from typing import Generator, Optional
import pyaudio
import numpy as np
import numpy.typing as npt
from pyaudio import Stream
from pydantic import BaseModel, PrivateAttr
import numpy

# REF: https://gist.github.com/mabdrabo/8678538
FORMAT = pyaudio.paFloat32


class Recorder(BaseModel):
    audio: pyaudio.PyAudio
    frames_per_buffer: int
    sample_freq: int
    _stream: Optional[Stream] = PrivateAttr()

    class Config:
        arbitrary_types_allowed = True

    def start(self):
        self._stream = self.audio.open(
            format=FORMAT,
            channels=1,
            rate=self.sample_freq,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.frames_per_buffer,
        )

    def stop(self):
        self._stream.stop_stream()
        self._stream.close()

    @functools.cached_property
    def device_index(self) -> int:
        for i in range(self.audio.get_device_count()):
            devinfo = self.audio.get_device_info_by_index(i)
            print("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in str(devinfo["name"]).lower():
                    print("Found an input: device %d - %s" % (i, devinfo["name"]))
                    return i

        raise Exception("No input device found.")

    def __iter__(self) -> Generator[npt.NDArray[np.float32], None, None]:  # type: ignore
        while True:
            yield self.get_buffer()

    def get_buffer(self) -> npt.NDArray[np.float32]:
        """REF: https://stackoverflow.com/questions/19629496/get-an-audio-sample-as-float-number-from-pyaudio-stream # noqa"""
        assert self._stream is not None, "Stream is None. Forgot to call start()?"
        data = self._stream.read(self.frames_per_buffer)
        decoded = numpy.fromstring(data, np.float32)  # type: ignore
        return decoded


class Player(BaseModel):
    audio: pyaudio.PyAudio
    volume: float
    duration: float
    frequency: float
    sample_freq: int

    class Config:
        arbitrary_types_allowed = True

    def play_sound(self) -> None:
        """REF: https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python"""
        stream = self.audio.open(
            format=FORMAT, channels=1, rate=self.sample_freq, output=True
        )

        # generate samples, note conversion to float32 array
        samples = (
            np.sin(
                2
                * np.pi
                * np.arange(self.sample_freq * self.duration)
                * self.frequency
                / self.sample_freq
            )
        ).astype(np.float32)

        # play. May repeat with different volume values (if done interactively)
        stream.write(self.volume * samples)

        # Close the stream
        stream.stop_stream()
        stream.close()
