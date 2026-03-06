from macinput import keyboard


def test_paste_text_restores_clipboard(monkeypatch):
    calls: list[tuple[str, object]] = []

    def fake_run(args, check, capture_output=False, input=None):
        calls.append((args[0], input))
        if args == ["pbpaste"]:
            class Result:
                returncode = 0
                stdout = b"original"

            return Result()

        class Result:
            returncode = 0
            stdout = b""

        return Result()

    def fake_press_key(key, modifiers=None, hold=0.0):
        calls.append(("press_key", (key, modifiers, hold)))

    monkeypatch.setattr(keyboard.subprocess, "run", fake_run)
    monkeypatch.setattr(keyboard, "press_key", fake_press_key)

    keyboard.paste_text("google.com")

    assert calls == [
        ("pbpaste", None),
        ("pbcopy", b"google.com"),
        ("press_key", ("v", ["command"], 0.0)),
        ("pbcopy", b"original"),
    ]


def test_paste_text_can_skip_clipboard_restore(monkeypatch):
    calls: list[tuple[str, object]] = []

    def fake_run(args, check, capture_output=False, input=None):
        calls.append((args[0], input))

        class Result:
            returncode = 0
            stdout = b""

        return Result()

    def fake_press_key(key, modifiers=None, hold=0.0):
        calls.append(("press_key", (key, modifiers, hold)))

    monkeypatch.setattr(keyboard.subprocess, "run", fake_run)
    monkeypatch.setattr(keyboard, "press_key", fake_press_key)

    keyboard.paste_text("google.com", restore_clipboard=False)

    assert calls == [
        ("pbcopy", b"google.com"),
        ("press_key", ("v", ["command"], 0.0)),
    ]
