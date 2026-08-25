# plant_health_status package tests (also discoverable by repo pytest)

from plant_health_status.heartbeat import format_status_message, parse_status_message


def test_format_increments_are_caller_owned() -> None:
    first = format_status_message(sequence=0, timestamp_iso="t0")
    second = format_status_message(sequence=1, timestamp_iso="t1")
    assert parse_status_message(first)["seq"] == "0"
    assert parse_status_message(second)["seq"] == "1"
