from setuptools import setup

setup(
    name="redundant_recognizer",
    entry_points={
        "console_scripts": ["redundant_recognizer=redundant_recognizer.main:main"],
    },
    install_requires=[
        "PySide6",
        "PySimpleGUI",
        "PySimpleGUIQt",
        "pyaudio",
        "vosk",
    ],
)
