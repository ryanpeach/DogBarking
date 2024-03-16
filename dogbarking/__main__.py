from typing import Annotated
from datetime import datetime
import pyaudio
import toml
import typer
from typer_config import use_toml_config

from dogbarking.audio import Player, Recorder
from dogbarking.math import get_rms

app = typer.Typer()


@app.command()
@use_toml_config
def nogui(
    volume: Annotated[float, "The percentage volume, must be between 0 and 1."] = 1.0,
    thresh: Annotated[float, "The threshold for the sound when playing."] = 0.0001,
    frequency: Annotated[float, "The frequency to play for the dog."] = 17000.0,
    duration: Annotated[float, "The duration to play the sound."] = 1.0,
    sample_freq: Annotated[int, "The sample rate in Hz."] = 44100,
    chunk: Annotated[int, "The number of frames per buffer."] = 10240,
    channels: Annotated[int, "The number of audio channels."] = 1,
    # email: Annotated[Optional[str], "The email to send the alert to."]=None
):
    # Start Recording
    audio = pyaudio.PyAudio()
    p = Player(audio, volume=volume, duration=duration, freq=frequency, fs=sample_freq)
    r = Recorder(
        audio,
        channels=channels,
        sample_freq=sample_freq,
        input=True,
        frames_per_buffer=chunk,
    )
    r.start()

    # If the rms of the waveform is greater than the threshold, play the sound
    for waveform in r:
        rms = get_rms(waveform)
        print(f"RMS: {rms}")
        if rms > thresh:
            p.start()
            p.play_sound()
            p.stop()
            print(f"Dog Barking at {datetime.now()}")


if __name__ == "__main__":
    pyproject_toml = toml.load("pyproject.toml")
    NAME = pyproject_toml["tool"]["poetry"]["name"]
    DESCRIPTION = pyproject_toml["tool"]["poetry"]["description"]
    app()
