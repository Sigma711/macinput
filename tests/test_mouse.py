from macinput import mouse


def test_scroll_posts_two_axis_event(monkeypatch):
    calls: list[tuple[str, object]] = []

    def fake_create_scroll_event(source, unit, wheel_count, vertical, horizontal):
        calls.append(("create", (source, unit, wheel_count, vertical, horizontal)))
        return "scroll-event"

    def fake_post(tap, event):
        calls.append(("post", (tap, event)))

    monkeypatch.setattr(mouse.Quartz, "CGEventCreateScrollWheelEvent", fake_create_scroll_event)
    monkeypatch.setattr(mouse.Quartz, "CGEventPost", fake_post)

    mouse.scroll(vertical=4, horizontal=-2)

    assert calls[0][0] == "create"
    assert calls[0][1][2:] == (2, 4, -2)
    assert calls[1] == ("post", (mouse.Quartz.kCGHIDEventTap, "scroll-event"))


def test_scroll_is_noop_for_zero_delta(monkeypatch):
    monkeypatch.setattr(
        mouse.Quartz,
        "CGEventCreateScrollWheelEvent",
        lambda *args: (_ for _ in ()).throw(AssertionError("should not be called")),
    )

    mouse.scroll(vertical=0, horizontal=0)
