import argparse
import audioop
import http.server
import json
import pyaudio
import threading
import time

import redundant_recognizer.recognizer
import redundant_recognizer.ui

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

        redundant_recognizer.ui.clear_ui()

        # Sleep for a bit, to let the audio loop catch up on recent samples.
        time.sleep(0.2)
        if "Content-Length" not in self.headers:
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers["Content-Length"])
        talon_phrase = self.rfile.read(length).decode("ascii").lower()
        self.send_response(200)
        self.end_headers()
        if talon_phrase == "kill redundant recognizer":
            redundant_recognizer.ui.stop_ui()
            return
        print(f"Talon phrase: {talon_phrase}")
        alternatives = recognizer.get_alternatives()
        if not alternatives:
            return
        


        redundant_recognizer.ui.populate_ui(talon_phrase, alternatives)

        self.wfile.write(json.dumps(alternatives).encode("ascii"))


def serve_http(port):
    http.server.HTTPServer(("", port), RequestHandler).serve_forever()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", type=int, required=True, help="port which HTTP server will bind to"
    )
    parser.add_argument("--model", type=str, required=True, help="path to a vosk model")
    return parser.parse_args()


def main():
    args = parse_args()
    threading.Thread(target=lambda: audio_loop(args.model), daemon=True).start()
    threading.Thread(target=lambda: serve_http(args.port), daemon=True).start()
    redundant_recognizer.ui.ui_loop()
