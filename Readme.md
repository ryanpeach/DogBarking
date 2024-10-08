# Dog Barking

A simple app for recording audio, and playing a frequency when the volume in the room is over some threshold.

This app has many uses, but is made originally for training a dog to stop barking. By playing a high pitched loud sound whenever my computer detected high volume noise, I trained my dog to stop barking while I was gone.

It will also email you about events with recordings and summarize the events throughout the day.

# Installation

You'll want to start by installing python and [poetry](https://python-poetry.org/docs/#installation) on your system. Do this however you see fit.

```bash
# If you are on macosx, be sure to do this, otherwise skip
brew install portaudio

# On ubuntu you might need to do
sudo apt install portaudio19-dev

# Then just install the requirements with poetry
poetry install

# Then install pre-commit (only if you are contributing)
pre-commit install
```

# Usage

> ./run.sh

**NOTE**: Only tapping CTRL+C *twice* will stop the app using this script.

This will start the app and record audio from your default input device. When the volume is over the threshold, it will play a high pitched sound.

# Email

To send an email to yourself, you need to create a file called `config.toml` in the root of the project. It should look like this:

```toml
sender_email = ""
receiver_email = ""
smtp_server = ""
smtp_password = ""
smtp_port = 1234
```

Do not share this as it contains your email password.
Optionally, you can exclude your password from this file and set it in your environment variables as `DOGBARKING_SMTP_PASSWORD`.

Now you need an smtp compatible email provider. I recommend https://www.mailgun.com/ as you can send to 5 authorized emails for free and it was easy to set up.

For mailgun your `config.toml` would look like this:

```toml
smtp_server = "smtp.mailgun.org"
smtp_port = 465
sender_email = "Mailgun Sandbox <postmaster@sandbox*.mailgun.org>" # Just an example
receiver_email = ""
smtp_password = ""
```
