import difflib
import queue
#import tkinter
#import tkinter.font
import PySimpleGUI as sg

#_root: tkinter.Tk
#_after_id = None
#_normal_font: tkinter.font.Font
#_bold_font: tkinter.font.Font

_NORMAL_FONT = ('Courier', 12, '')
_BOLD_FONT = ('Courier', 12, 'bold')

_queue =queue.Queue(maxsize=100) 

_stopped: bool = False

def ui_loop():
    sg.theme('LightGray1')
    global _root, _normal_font, _bold_font
    global _queue, _stopped
    layout=sg.Frame('Title', [], key="-FRAME-")
    window = sg.Window("Transcriptions", layout=[[sg.Text(text="hello", visible=False, key="-TEXT-")]], finalize=True, use_default_focus=False, no_titlebar=True)
    talon_phrase, alternatives = _queue.get()
    while not _stopped:
        layout, timeout = get_layout(talon_phrase, alternatives)
        window["-TEXT-"].update(alternatives[0], visible=True)
        window.reappear()
        window.refresh()
        try:
            talon_phrase, alternatives = _queue.get(timeout=timeout)
        except queue.Empty:
            window.disappear()
            window.refresh()
            talon_phrase, alternatives = _queue.get()


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


def populate_ui(talon_phrase, alternatives):
    global _queue
    _queue.put((talon_phrase, alternatives))


def get_layout(talon_phrase, alternatives):
    #global _root, _after_id
    talon_words = talon_phrase.split(" ")
    layout = []
    for i, a in enumerate(alternatives):
        layout.append(_add_alternative(i, talon_words, a.split(" ")))

    #_root.geometry("-25+25")
    timeout_ms = 5.0 + 0.025 * sum(len(a) for a in alternatives)
    
    return layout, timeout_ms


def stop_ui():
    global _stopped
    _stopped = True # _root.destroy()

def _add_alternative(index, talon_words, alternative_words):
    #global _root, _bold_font, _normal_font

    #frame = tkinter.Frame(_root, pady=5)
    #frame.pack(side="top", fill="x")
    #tkinter.Label(frame, text=f"{index}. ", font=_normal_font).pack(side="left")

    result = [
        _text(text=f"{index}. ", font=_NORMAL_FONT)
    ]

    matcher = difflib.SequenceMatcher(a=talon_words, b=alternative_words)
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
            result.append(
                _text(
                    text=f"{leading}{unmatched}",
                    font=_BOLD_FONT
                )
            )
        elif match_talon_index > talon_index:
            # Alternative removes words
            leading = " " if alt_index > 0 else ""
            result.append(
                _text(
                    text=f"{leading}__",
                    font=_BOLD_FONT
                )
            )

        alt_index = match_alt_index
        talon_index = match_talon_index

        if match_length > 0:
            leading = " " if alt_index > 0 else ""
            matched = " ".join(
                alternative_words[match_alt_index : match_alt_index + match_length]
            )
            result.append(
                _text(
                    text=f"{leading}{matched}",
                    font=_NORMAL_FONT
                )
            )
            alt_index += match_length
            talon_index += match_length
    return result

def _text(text, font):
    return sg.Text(
                    text=text,
                    font=font,
                    pad=0,
                    justification='left',
                )