import functools
from pathlib import Path
from typing import Generator, List, Optional
import pyaudio
import numpy as np
import numpy.typing as npt
from pyaudio import Stream
from pydantic import BaseModel, PrivateAttr
import numpy
from loguru import logger
import soundfile as sf
import os

# REF: https://gist.github.com/mabdrabo/8678538
FORMAT = pyaudio.paFloat32


class Recorder(BaseModel):
    audio: pyaudio.PyAudio
    frames_per_buffer: int
    sample_freq: int
    keep_historical_buffers: int
    _stream: Optional[Stream] = PrivateAttr()
    _waveform: Optional[List[npt.NDArray[np.float32]]] = PrivateAttr()

    class Config:
        arbitrary_types_allowed = True

    def start(self):
        self._waveform = []
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
            logger.info("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in str(devinfo["name"]).lower():
                    logger.info("Found an input: device %d - %s" % (i, devinfo["name"]))
                    return i

        raise Exception("No input device found.")

    def __iter__(self) -> Generator[npt.NDArray[np.float32], None, None]:  # type: ignore
        while True:
            out = self.get_buffer()
            if self._waveform is None:
                self._waveform = []
            elif len(self._waveform) > self.keep_historical_buffers:
                self._waveform.pop(0)
            self._waveform.append(out)
            yield out

    def get_buffer(self) -> npt.NDArray[np.float32]:
        """REF: https://stackoverflow.com/questions/19629496/get-an-audio-sample-as-float-number-from-pyaudio-stream # noqa"""
        assert self._stream is not None, "Stream is None. Forgot to call start()?"
        data = self._stream.read(self.frames_per_buffer)
        decoded = numpy.fromstring(data, np.float32)  # type: ignore
        return decoded

    def save(self, filepath: Path) -> None:
        """Save the recorded waveform to an mp3 file."""
        # If directory doesn't exist, create it
        directory = filepath.parent
        if not directory.exists():
            os.makedirs(directory)

        if self._waveform is None:
            logger.error("No waveform to save.")
            return

        waveform = np.concatenate(self._waveform)
        sf.write(filepath, waveform, self.sample_freq)
        logger.info(f"Saved {filepath}")


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
