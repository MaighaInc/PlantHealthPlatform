"""Mock GPIO for SIMULATION / DEVELOPMENT / CI (PHP-17)."""

from __future__ import annotations

from dataclasses import dataclass

from plant_health_irrigation.interfaces import GPIOInterface, PinState


@dataclass(frozen=True)
class PinTransition:
    pin: int
    state: PinState
    seq: int


class MockGPIO(GPIOInterface):
    """In-memory GPIO that records every pin transition for tests."""

    def __init__(self) -> None:
        self._states: dict[int, PinState] = {}
        self._configured: set[int] = set()
        self._transitions: list[PinTransition] = []
        self._seq = 0
        self._cleaned = False

    @property
    def transitions(self) -> tuple[PinTransition, ...]:
        return tuple(self._transitions)

    def setup_output(self, pin: int, *, initial: PinState = PinState.LOW) -> None:
        self._assert_not_cleaned()
        pin_i = int(pin)
        self._configured.add(pin_i)
        self._write_unchecked(pin_i, initial)

    def write(self, pin: int, state: PinState) -> None:
        self._assert_not_cleaned()
        pin_i = int(pin)
        if pin_i not in self._configured:
            raise RuntimeError(f"pin {pin_i} not configured; call setup_output first")
        self._write_unchecked(pin_i, state)

    def read(self, pin: int) -> PinState:
        pin_i = int(pin)
        if pin_i not in self._states:
            raise RuntimeError(f"pin {pin_i} has no known state")
        return self._states[pin_i]

    def cleanup(self) -> None:
        for pin in sorted(self._configured):
            self._write_unchecked(pin, PinState.LOW)
        self._cleaned = True

    def _write_unchecked(self, pin: int, state: PinState) -> None:
        prev = self._states.get(pin)
        self._states[pin] = state
        if prev != state:
            self._seq += 1
            self._transitions.append(PinTransition(pin=pin, state=state, seq=self._seq))

    def _assert_not_cleaned(self) -> None:
        if self._cleaned:
            raise RuntimeError("MockGPIO already cleaned up")
