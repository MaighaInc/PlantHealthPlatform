"""GPIO port — irrigation actuation depends on this, not RPi drivers (PHP-17)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class PinState(str, Enum):
    LOW = "low"
    HIGH = "high"


class GPIOInterface(ABC):
    """Hardware-agnostic digital output contract."""

    @abstractmethod
    def setup_output(self, pin: int, *, initial: PinState = PinState.LOW) -> None:
        """Configure ``pin`` as an output (startup-safe default LOW)."""

    @abstractmethod
    def write(self, pin: int, state: PinState) -> None:
        """Drive ``pin`` to ``state``."""

    @abstractmethod
    def read(self, pin: int) -> PinState:
        """Return last commanded / known state for ``pin``."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release pins; leave outputs in a safe OFF state when possible."""
