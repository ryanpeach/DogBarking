from pathlib import Path
from typing import Annotated
from datetime import datetime
import pyaudio
import toml
import typer
from typer_config import use_toml_config

from dogbarking.audio import Player, Recorder
from dogbarking.math import get_rms
from loguru import logger

app = typer.Typer()


@app.command()
@use_toml_config()
def nogui(
    volume: Annotated[
        float, typer.Argument(help="The volume to play the sound at.", min=0.0, max=1.0)
    ] = 1.0,
    thresh: Annotated[
        float,
        typer.Argument(help="The threshold to trigger the sound.", min=0.0, max=1.0),
    ] = 0.1,
    frequency: Annotated[
        float, typer.Argument(help="The frequency of the sound to play.", min=0.0)
    ] = 17000.0,
    duration: Annotated[
        float,
        typer.Argument(help="The duration to play the sound in seconds.", min=0.0),
    ] = 5.0,
    sample_freq: Annotated[
        int, typer.Argument(help="The sample rate in Hz.", min=0)
    ] = 44100,
    keep_historical_seconds: Annotated[
        int, typer.Argument(help="The number of seconds to save to audio.", min=0)
    ] = 10,
    seconds_per_buffer: Annotated[
        float, typer.Argument(help="The number of seconds per buffer.", min=0.0)
    ] = 0.1,
    save_path: Annotated[
        Path, typer.Argument(help="The path to save the audio file to.")
    ] = Path("./outputs"),
    # email: Annotated[Optional[str], "The email to send the alert to."]=None
):
    logger.warning("Remember to turn your volume all the way up!")

    # Start Recording
    audio = pyaudio.PyAudio()
    p = Player(
        audio=audio,
        volume=volume,
        duration=duration,
        sample_freq=sample_freq,
        frequency=frequency,
    )
    r = Recorder(
        audio=audio,
        keep_historical_buffers=int(keep_historical_seconds / seconds_per_buffer),
        sample_freq=sample_freq,
        frames_per_buffer=int(sample_freq * seconds_per_buffer),
    )
    r.start()

    # If the rms of the waveform is greater than the threshold, play the sound
    for waveform in r:
        rms = get_rms(waveform)
        logger.debug(f"RMS: {rms}")
        if rms > thresh:
            logger.info(f"Dog Barking at {datetime.now()}")

            # Stop the recording, don't want to record the sound we are playing
            r.stop()

            # Save the recording
            filename = save_path / f"{datetime.now().isoformat()}.mp3"
            r.save(filename)

            # Play the sound
            p.play_sound()

            # Start recording again
            r.start()


if __name__ == "__main__":
    pyproject_toml = toml.load("pyproject.toml")
    NAME = pyproject_toml["tool"]["poetry"]["name"]
    DESCRIPTION = pyproject_toml["tool"]["poetry"]["description"]
    app()
