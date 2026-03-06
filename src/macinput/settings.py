"""Runtime settings for the MCP server."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class ServerSettings:
    default_screenshot_ttl: float = 30.0
    max_screenshot_ttl: float = 300.0
    max_typing_length: int = 2000
    min_action_delay: float = 0.05
    default_typing_interval: float = 0.02

    @classmethod
    def from_env(cls) -> "ServerSettings":
        return cls(
            default_screenshot_ttl=_env_float("MACINPUT_DEFAULT_SCREENSHOT_TTL", 30.0),
            max_screenshot_ttl=_env_float("MACINPUT_MAX_SCREENSHOT_TTL", 300.0),
            max_typing_length=_env_int("MACINPUT_MAX_TYPING_LENGTH", 2000),
            min_action_delay=_env_float("MACINPUT_MIN_ACTION_DELAY", 0.05),
            default_typing_interval=_env_float("MACINPUT_DEFAULT_TYPING_INTERVAL", 0.02),
        ).validate()

    def validate(self) -> "ServerSettings":
        if self.default_screenshot_ttl < 0:
            raise ValueError("default_screenshot_ttl must be >= 0")
        if self.max_screenshot_ttl < self.default_screenshot_ttl:
            raise ValueError("max_screenshot_ttl must be >= default_screenshot_ttl")
        if self.max_typing_length <= 0:
            raise ValueError("max_typing_length must be > 0")
        if self.min_action_delay < 0:
            raise ValueError("min_action_delay must be >= 0")
        if self.default_typing_interval < 0:
            raise ValueError("default_typing_interval must be >= 0")
        return self

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)
