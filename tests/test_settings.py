from macinput.settings import ServerSettings


def test_settings_validate_success():
    settings = ServerSettings(
        default_screenshot_ttl=10.0,
        max_screenshot_ttl=20.0,
        max_typing_length=100,
        min_action_delay=0.01,
        default_typing_interval=0.02,
    )
    assert settings.validate() is settings


def test_settings_reject_invalid_ttl_order():
    settings = ServerSettings(default_screenshot_ttl=30.0, max_screenshot_ttl=20.0)
    try:
        settings.validate()
    except ValueError as exc:
        assert "max_screenshot_ttl" in str(exc)
    else:
        raise AssertionError("validate() should reject invalid ttl ordering")
