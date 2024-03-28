import difflib
import queue

# import tkinter
# import tkinter.font
import PySimpleGUI as sg

# _root: tkinter.Tk
# _after_id = None
# _normal_font: tkinter.font.Font
# _bold_font: tkinter.font.Font

_NORMAL_FONT = ("Courier", 12, "")
_BOLD_FONT = ("Courier", 12, "bold")

_NUM_ROWS = 15
_NUM_TEXTS_PER_ROW = 12

_queue = queue.Queue(maxsize=100)

_stopped: bool = False


def ui_loop():
    sg.theme("LightGray1")
    global _queue, _stopped
    window = sg.Window(
        "Transcriptions",
        layout=_initial_layout(),
        finalize=True,
        use_default_focus=False,
        no_titlebar=True,
        keep_on_top=True,
        text_justification="left",
        element_padding=0,
        auto_size_text=True,
    )
    talon_phrase, alternatives = _queue.get()
    while not _stopped:
        timeout = get_layout(window, talon_phrase, alternatives)
        # window["-TEXT-"].update(alternatives[0], visible=True
        window.reappear()
        window.refresh()
        try:
            talon_phrase, alternatives = _queue.get(timeout=timeout)
        except queue.Empty:
            window.disappear()
            window.refresh()
            talon_phrase, alternatives = _queue.get()


def _initial_layout():
    return [
        [
            sg.pin(sg.Text(text="", visible=False, key=_text_key(i, j)))
            for j in range(_NUM_TEXTS_PER_ROW)
        ]
        for i in range(_NUM_ROWS)
    ]


def _clear_root():
    global _root
    for c in list(_root.children.values()):
        c.destroy()
    _root.withdraw()


def clear_ui():
    pass
    # global _root, _after_id
    # _clear_root()
    # if _after_id:
    #     _root.after_cancel(_after_id)


def _text_key(i, j):
    return f"-TEXT:{i}:{j}-"


def populate_ui(talon_phrase, alternatives):
    global _queue
    _queue.put((talon_phrase, alternatives))


def get_layout(window, talon_phrase, alternatives):
    # global _root, _after_id
    talon_words = talon_phrase.split(" ")
    layout = []
    for i, a in enumerate(alternatives):
        layout.append(_add_alternative(window, i, talon_words, a.split(" ")))
    for i in range(len(alternatives), _NUM_ROWS):
        for j in range(_NUM_TEXTS_PER_ROW):
            t=            window[_text_key(i, j)]
            t.update("", visible=False)
            # t.set_size((0,0))

    # _root.geometry("-25+25")
    timeout_ms = 5.0 + 0.025 * sum(len(a) for a in alternatives)

    return timeout_ms


def stop_ui():
    global _stopped
    _stopped = True  # _root.destroy()


def _add_alternative(window, index, talon_words, alternative_words):
    # global _root, _bold_font, _normal_font

    # frame = tkinter.Frame(_root, pady=5)
    # frame.pack(side="top", fill="x")
    # tkinter.Label(frame, text=f"{index}. ", font=_normal_font).pack(side="left")

    window[_text_key(index, 0)].update(f"{index}. ", visible=True, font=_NORMAL_FONT)

    matcher = difflib.SequenceMatcher(a=talon_words, b=alternative_words)
    text_index = 1
    talon_index = 0
    alt_index = 0
    for (
        match_talon_index,
        match_alt_index,
        match_length,
    ) in matcher.get_matching_blocks():
        if match_alt_index > alt_index:
            # Alternative adds or changes words
            leading = " " if alt_index > 0 else ""
            unmatched = " ".join(alternative_words[alt_index:match_alt_index])
            window[_text_key(index, text_index)].update(
                value=f"{leading}{unmatched}", font=_BOLD_FONT, visible=True
            )
            text_index += 1
        elif match_talon_index > talon_index:
            # Alternative removes words
            leading = " " if alt_index > 0 else ""
            window[_text_key(index, text_index)].update(
                value=f"{leading}__", font=_BOLD_FONT, visible=True
            )
            text_index += 1

        if text_index >= _NUM_TEXTS_PER_ROW:
            break

        alt_index = match_alt_index
        talon_index = match_talon_index

        if match_length > 0:
            leading = " " if alt_index > 0 else ""
            matched = " ".join(
                alternative_words[match_alt_index : match_alt_index + match_length]
            )
            window[_text_key(index, text_index)].update(
                value=f"{leading}{matched}", font=_NORMAL_FONT, visible=True
            )
            text_index += 1
            alt_index += match_length
            talon_index += match_length

        if text_index >= _NUM_TEXTS_PER_ROW:
            break

        for i in range(text_index, _NUM_TEXTS_PER_ROW):
            window[_text_key(index, i)].update(value="", visible=False)


def _text(text, font):
    return sg.Text(
        text=text,
        font=font,
        pad=0,
        justification="left",
    )
