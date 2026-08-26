"""Raspberry Pi GPIO backend — HARDWARE/PRODUCTION only (PHP-17)."""

from __future__ import annotations

from plant_health_irrigation.interfaces import GPIOInterface, PinState


class RaspberryPiGPIOError(RuntimeError):
    """Raised when real Pi GPIO is unavailable or misused."""


class RaspberryPiGPIO(GPIOInterface):
    """
    Thin wrapper around ``RPi.GPIO``.

    Not imported at module load — only when constructed — so CI/SIMULATION
    hosts never require the library.
    """

    def __init__(self, *, mode: str = "BCM") -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RaspberryPiGPIOError(
                "RPi.GPIO is not installed; use MockGPIO in SIMULATION/DEVELOPMENT"
            ) from exc
        self._GPIO = GPIO
        mode_n = mode.strip().upper()
        if mode_n == "BCM":
            GPIO.setmode(GPIO.BCM)
        elif mode_n == "BOARD":
            GPIO.setmode(GPIO.BOARD)
        else:
            raise RaspberryPiGPIOError(f"unsupported GPIO mode: {mode!r}")
        self._configured: set[int] = set()
        self._states: dict[int, PinState] = {}

    def setup_output(self, pin: int, *, initial: PinState = PinState.LOW) -> None:
        pin_i = int(pin)
        initial_level = self._GPIO.HIGH if initial is PinState.HIGH else self._GPIO.LOW
        self._GPIO.setup(pin_i, self._GPIO.OUT, initial=initial_level)
        self._configured.add(pin_i)
        self._states[pin_i] = initial

    def write(self, pin: int, state: PinState) -> None:
        pin_i = int(pin)
        if pin_i not in self._configured:
            raise RaspberryPiGPIOError(f"pin {pin_i} not configured")
        level = self._GPIO.HIGH if state is PinState.HIGH else self._GPIO.LOW
        self._GPIO.output(pin_i, level)
        self._states[pin_i] = state

    def read(self, pin: int) -> PinState:
        pin_i = int(pin)
        if pin_i not in self._states:
            raise RaspberryPiGPIOError(f"pin {pin_i} has no known state")
        return self._states[pin_i]

    def cleanup(self) -> None:
        for pin in sorted(self._configured):
            try:
                self._GPIO.output(pin, self._GPIO.LOW)
            except Exception:  # noqa: BLE001
                pass
            self._states[pin] = PinState.LOW
        self._GPIO.cleanup()
        self._configured.clear()
