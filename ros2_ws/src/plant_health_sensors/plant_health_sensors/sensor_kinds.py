"""Sensor kind identifiers and default ROS topics for PlantHealthPlatform."""

from __future__ import annotations

from enum import Enum


class SensorKind(str, Enum):
    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    CO2 = "co2"


# Canonical topics (documented in ROS_ARCHITECTURE.md)
DEFAULT_TOPICS: dict[SensorKind, str] = {
    SensorKind.SOIL_MOISTURE: "/soil/moisture",
    SensorKind.TEMPERATURE: "/environment/temperature",
    SensorKind.HUMIDITY: "/environment/humidity",
    SensorKind.LIGHT: "/environment/light",
    SensorKind.CO2: "/environment/co2",
}

# Plausible simulation defaults (units noted in comments)
DEFAULT_BASE_VALUES: dict[SensorKind, float] = {
    SensorKind.SOIL_MOISTURE: 45.0,  # %
    SensorKind.TEMPERATURE: 24.0,  # °C
    SensorKind.HUMIDITY: 55.0,  # %
    SensorKind.LIGHT: 800.0,  # arbitrary lux-like
    SensorKind.CO2: 420.0,  # ppm
}

DEFAULT_BOUNDS: dict[SensorKind, tuple[float, float]] = {
    SensorKind.SOIL_MOISTURE: (0.0, 100.0),
    SensorKind.TEMPERATURE: (-20.0, 60.0),
    SensorKind.HUMIDITY: (0.0, 100.0),
    SensorKind.LIGHT: (0.0, 100_000.0),
    SensorKind.CO2: (0.0, 5000.0),
}
