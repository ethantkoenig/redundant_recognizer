import argparse
import audioop
import fcntl
import http.server
import json
import os
import threading
import time

import pyaudio

import redundant_recognizer.recognizer

recognizer: redundant_recognizer.recognizer.Recognizer


def create_mic_stream():
    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192,
    )
    stream.start_stream()
    return stream


def audio_loop(model_path):
    global recognizer
    recognizer = redundant_recognizer.recognizer.Recognizer(model_path)
    stream = create_mic_stream()
    quiet_since = None
    while True:
        data = stream.read(4096)
        amp = audioop.rms(data, 2)
        if amp < 500:
            if not quiet_since:
                quiet_since = time.time()
            elif quiet_since < time.time() - 4:
                recognizer.reset()
                print("^", end="", flush=True)
                continue
        else:
            quiet_since = None
        print(".", end="", flush=True)
        recognizer.accept(data)


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global recognizer

        # Sleep for a bit, to let the audio loop catch up on recent samples.
        time.sleep(0.2)

        self.send_response(200)
        self.end_headers()

        alternatives = recognizer.get_alternatives()

        self.wfile.write(json.dumps(alternatives).encode("ascii"))


def serve_http(port):
    http.server.HTTPServer(("", port), RequestHandler).serve_forever()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", type=int, required=True, help="port which HTTP server will bind to"
    )
    parser.add_argument("--model", type=str, required=True, help="path to a vosk model")
    parser.add_argument(
        "--pidfile",
        type=str,
        help="path to a pid file that the process will lock and write",
    )
    return parser.parse_args()


def lock_and_write_pid_file(path: str):
    # Note: need to store file object in a global, otherwise it gets garbage
    # collected and the lock is released.
    global file
    file = open(path, "a+")
    try:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        raise RuntimeError(f"Failed to lock {path}") from e

    file.seek(0)
    file.truncate()
    file.write(f"{os.getpid()}\n")
    file.flush()


def main():
    args = parse_args()

    if args.pidfile:
        lock_and_write_pid_file(args.pidfile)

    threading.Thread(target=lambda: audio_loop(args.model), daemon=True).start()
    serve_http(args.port)
