import difflib
import tkinter
import tkinter.font

_root: tkinter.Tk
_after_id = None
_normal_font: tkinter.font.Font
_bold_font: tkinter.font.Font


def ui_loop():
    global _root, _normal_font, _bold_font
    _root = tkinter.Tk()
    _root.wm_attributes("-type", "splash")
    _root.wm_attributes("-alpha", 0.85)
    _root.geometry("-25+25")
    _normal_font = tkinter.font.Font()
    _bold_font = tkinter.font.Font(weight="bold")
    _root.mainloop()


def _clear_root():
    global _root
    for c in list(_root.children.values()):
        c.destroy()
    _root.withdraw()


def clear_ui():
    global _root, _after_id
    _clear_root()
    if _after_id:
        _root.after_cancel(_after_id)


def populate_ui(talon_phrase, alternatives):
    global _root, _after_id
    talon_words = talon_phrase.split(" ")
    for i, a in enumerate(alternatives):
        _add_alternative(i, talon_words, a.split(" "))

    _root.geometry("-25+25")
    timeout_ms = 5000 + 25 * sum(len(a) for a in alternatives)
    _after_id = _root.after(timeout_ms, _clear_root)

    _root.deiconify()
    _root.update_idletasks()


def _add_alternative(index, talon_words, alternative_words):
    global _root, _bold_font, _normal_font

    frame = tkinter.Frame(_root, pady=5)
    frame.pack(side="top", fill="x")
    tkinter.Label(frame, text=f"{index}. ", font=_normal_font).pack(side="left")

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
            tkinter.Label(frame, text=f"{leading}{unmatched}", font=_bold_font).pack(
                side="left"
            )
        elif match_talon_index > talon_index:
            # Alternative removes words
            leading = " " if alt_index > 0 else ""
            tkinter.Label(frame, text=f"{leading}__", font=_bold_font).pack(side="left")

        alt_index = match_alt_index
        talon_index = match_talon_index

        if match_length > 0:
            leading = " " if alt_index > 0 else ""
            matched = " ".join(
                alternative_words[match_alt_index : match_alt_index + match_length]
            )
            tkinter.Label(frame, text=f"{leading}{matched}", font=_normal_font).pack(
                side="left"
            )
            alt_index += match_length
            talon_index += match_length
