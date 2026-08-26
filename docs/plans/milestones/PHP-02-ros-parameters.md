# PHP-02 — ROS Parameters and Runtime Configuration

## Goal

Make status nodes configurable without code changes: validated ROS parameters, YAML + launch overrides, and shared env/mode helpers.

## Prerequisites

- PHP-01 complete

## Acceptance Criteria

- [x] `publish_period_sec`, `topic`, `source` validated at startup (fail on invalid)
- [x] Parameter YAML `config/status_params.yaml` installed with package
- [x] Launch accepts `params_file` and `publish_period_sec` overrides
- [x] Shared `DEVELOPMENT_MODE` / `.env` helpers under `shared/plant_health_common`
- [x] Unit tests: invalid params rejected; valid params applied; mode parsing
- [x] CONFIGURATION.md and README updated

## Architecture Impact

```text
.env / DEVELOPMENT_MODE  →  plant_health_common
ROS params / YAML / launch → StatusPublisherParams / StatusSubscriberParams → nodes
```

## Files

- `plant_health_status/parameters.py`
- `plant_health_status/config/status_params.yaml`
- `shared/plant_health_common/`
- `tests/unit/test_parameters.py`, `test_runtime_config.py`

## Tests

```bash
export PYTHONPATH=ros2_ws/src/plant_health_status:shared
python -m pytest tests/unit -q
```

ROS host override example:

```bash
ros2 launch plant_health_status status.launch.py publish_period_sec:=0.5
ros2 param get /status_publisher publish_period_sec
```

## Intern Learning Outcomes

- Why validate parameters at startup?
- Difference between env config and ROS parameters?
- How to change behavior without editing node code?
