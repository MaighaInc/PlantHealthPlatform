# Development Running Log

> Session notes for PlantHealthPlatform. Append after meaningful work sessions.

---

## 2026-08-25 — PHP-01 start

- Created feature branch `feature/php-01-ros-foundation`
- Accepted ADR-0001: ROS 2 Humble
- Bootstrapped `.env.example`, `pyproject.toml`, `ros2_ws/`
- Implemented `plant_health_status` publisher + subscriber on `/system/status`
- Hardware-free unit tests for heartbeat format/parse
- Native ROS not available on Windows host — full launch smoke deferred to WSL/Ubuntu Humble
