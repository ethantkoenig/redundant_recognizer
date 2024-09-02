import json
import re
import threading
import vosk

_phrase_commands = [
    "all cap",
    "all lower",
    "camel",
    "hammer",
    "kebab",
    "say",
    "sentence",
    "smash",
    "snake",
    "title",
]

_phrase_command_mistakes = {
    "say": ["day", "said", "same", "they"],
}

_phrase_command_triggers = {
    **{c: c for c in _phrase_commands},
    **{
        mistake: command
        for (command, mistakes) in _phrase_command_mistakes.items()
        for mistake in mistakes
    },
}

_word_commands = ["word"]

_word_command_triggers = {
    **{c: c for c in _word_commands},
}

_all_command_triggers = {
    **_phrase_command_triggers,
    **_word_command_triggers,
}

_phrase_pattern = re.compile(rf"\b({'|'.join(_phrase_command_triggers)}) (.*)$")

_word_pattern = re.compile(rf"\b({'|'.join(_word_command_triggers)}) ([^ ]*)$")


def _command(alternative):
    match = _phrase_pattern.search(alternative) or _word_pattern.search(alternative)
    if match is None:
        return None
    command = _all_command_triggers[match.group(1)]
    return f"{command} {match.group(2)}"


class Recognizer:
    def __init__(self, model_path):
        model = vosk.Model(model_path)
        self._recognizer = vosk.KaldiRecognizer(model, 16000)
        self._recognizer.SetMaxAlternatives(20)
        self._lock = threading.Lock()  # guards _recognizer

    def reset(self):
        with self._lock:
            self._recognizer.Reset()

    def accept(self, data):
        with self._lock:
            self._recognizer.AcceptWaveform(data)

    def get_alternatives(self):
        with self._lock:
            raw_result = self._recognizer.FinalResult()
            self._recognizer.Reset()
        print(raw_result)
        result = json.loads(raw_result)
        if "alternatives" not in result:
            return []
        alternatives = [_command(a["text"]) for a in result["alternatives"]]
        # Order-preserving dedupe
        return list(dict.fromkeys(a for a in alternatives if a))
