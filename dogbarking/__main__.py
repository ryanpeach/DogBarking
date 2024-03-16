from pathlib import Path
import textwrap
import sys
from typing import Annotated, Optional
from datetime import datetime
import pyaudio
from pydantic import SecretStr
import toml
import typer
from typer_config import use_toml_config

from dogbarking.audio import Player, Recorder
from dogbarking.email import Email, match_cron
from dogbarking.math import get_rms
import pandas as pd
from loguru import logger

app = typer.Typer()


@app.command()
@use_toml_config(default_value="config.toml")
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
    sender_email: Annotated[
        Optional[str], typer.Option(help="The email to send the alert from.")
    ] = None,
    receiver_email: Annotated[
        Optional[str], typer.Option(help="The email to send the alert to.")
    ] = None,
    smtp_password: Annotated[
        Optional[str],
        typer.Option(
            help="The password for the email.", envvar="DOGBARKING_SMTP_PASSWORD"
        ),
    ] = None,
    smtp_server: Annotated[
        Optional[str],
        typer.Option(
            help="The SMTP server to send the email.", envvar="DOGBARKING_SMTP_SERVER"
        ),
    ] = None,
    smtp_port: Annotated[
        Optional[int],
        typer.Option(
            help="The SMTP port to send the email.", envvar="DOGBARKING_SMTP_PORT"
        ),
    ] = 465,
    summary_cron: Annotated[
        str, typer.Option(help="The cron schedule to send a summary email.")
    ] = "*/30 * * * *",
    log_level: Annotated[
        str,
        typer.Option(
            help="The logging level to use.",
        ),
    ] = "INFO",
):
    """Dog Barking Alert System"""

    # Set up the logger
    logger.remove(0)
    logger.add(
        sys.stderr,
        level=log_level,
    )

    # Check that the email details are provided if any of them are provided
    use_email = any(
        [sender_email, receiver_email, smtp_password, smtp_server, smtp_port]
    )
    if use_email and not all(
        [sender_email, receiver_email, smtp_password, smtp_server, smtp_port]
    ):
        logger.error(
            "If you want to send an email, you need to provide all the details: sender_email, receiver_email, smtp_server, smtp_password, smtp_port"
        )
        raise typer.Abort()

    logger.warning("Remember to turn your volume all the way up!")

    # Send a start email
    if use_email:
        assert sender_email is not None
        assert receiver_email is not None
        assert smtp_password is not None
        assert smtp_server is not None
        assert smtp_port is not None
        Email(
            sender_email=sender_email,
            receiver_email=receiver_email,
            smtp_password=SecretStr(smtp_password),
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            summary=f"Dog Barking App Starting {datetime.now()}",
            body="The dog barking detection has started.",
        ).send_email()

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
    rms_history = []
    for waveform in r:
        rms = get_rms(waveform)
        logger.debug(f"RMS: {rms}")
        rms_history.append(rms)

        # Handle summary email
        # Do not track seconds
        if (
            match_cron(summary_cron)
            and use_email
            and len(rms_history) > 0
            and len(rms_history) % (int(1 / seconds_per_buffer) * 60) == 0
        ):
            r.stop()
            assert sender_email is not None
            assert receiver_email is not None
            assert smtp_password is not None
            assert smtp_server is not None
            assert smtp_port is not None
            Email(
                sender_email=sender_email,
                receiver_email=receiver_email,
                smtp_password=SecretStr(smtp_password),
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                summary=f"Dog Barking Summary Email {datetime.now()}",
                body=f"Here are some RMS statistics about the dog barking:\n{pd.DataFrame(rms_history).describe()}",
            ).send_email()
            r.start()
            rms_history = []

        # Handle thresholding
        if rms > thresh:
            logger.info(f"Dog Barking at {datetime.now()}")

            # Stop the recording, don't want to record the sound we are playing
            r.stop()

            # Play the sound
            p.play_sound()

            # Save the recording and send the email
            filepath = save_path / f"{datetime.now().isoformat()}.mp3"
            r.save(filepath)
            if use_email:
                assert sender_email is not None
                assert receiver_email is not None
                assert smtp_password is not None
                assert smtp_server is not None
                assert smtp_port is not None
                Email(
                    sender_email=sender_email,
                    receiver_email=receiver_email,
                    attachment_filepath=filepath,
                    smtp_password=SecretStr(smtp_password),
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    summary=f"Dog Barking Alert {datetime.now().isoformat()}",
                    body=textwrap.dedent(
                        f"""\
                        Your dog was barking at {datetime.now().isoformat()}.
                        """
                    ),
                ).send_email()

            # Start recording again
            r.start()


if __name__ == "__main__":
    pyproject_toml = toml.load("pyproject.toml")
    NAME = pyproject_toml["tool"]["poetry"]["name"]
    DESCRIPTION = pyproject_toml["tool"]["poetry"]["description"]
    app()
