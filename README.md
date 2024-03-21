# redundant_recognizer

A pipx-compatible executable that listens to microphone input and recognizes
Talon phrase commands (possibly with several alternative transcriptions).

This is intended to provide alternative transcriptions of an utterance in case
Talon's transcription is incorrect.

## Requirements

On Ubuntu/Debian, the following packages are required to install (via pipx) and run the application:

```
sudo apt install build-essential portaudio19-dev python3-tk
```
