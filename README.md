# redundant_recognizer

A pipx-compatible executable that listens to microphone input and recognizes
Talon phrase commands (possibly with several alternative transcriptions).

This is intended to provide alternative transcriptions of an utterance in case
Talon's transcription is incorrect.

## Requirements

Ubuntu/Debian:

```
sudo apt install build-essential portaudio19-dev
```

MacOS:

```
brew install portaudio
```