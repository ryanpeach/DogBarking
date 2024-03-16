# Dog Barking

A simple for recording audio, and playing a frequency when the volume is over some threshold.

This app has many uses, but is made originally for training a dog to stop barking. By playing a high pitched, loud sound whenever my computer detected high volume noise, I trained my dog to stop barking while i was gone.

# Installation

```bash
# If you are on macosx, be sure to do this, otherwise skip
brew install portaudio

# Then just install the requirements with poetry
poetry install

# Then install pre-commit (only if you are contributing)
pre-commit install
```

## Usage

> python3 -m dog_barking
