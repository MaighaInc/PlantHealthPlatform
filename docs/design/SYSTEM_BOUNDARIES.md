# System Boundaries

> Critical separations that must be preserved across all milestones

## Module Boundaries

```text
ROS              communication / orchestration
Hardware         physical device access
CV               image processing
ML               training / evaluation / inference
Health Engine    plant-health interpretation
Decision Engine  operational decision
Safety Layer     actuator protection
GPIO             physical actuation
Backend          persistence / API
Frontend         visualization / user interaction
```

Do not collapse all functionality into one application.

## Prediction ≠ Decision ≠ Actuation

This separation is **mandatory**.

| Layer | Example output |
|-------|----------------|
| **ML (Prediction)** | "Plant appears stressed." |
| **Decision Engine** | "Irrigation may be appropriate." |
| **Safety Layer** | "Conditions permit irrigation." |
| **GPIO (Actuation)** | "Activate pump." |

### Rules

- ML inference must **never** directly activate physical irrigation.
- Individual sensors must **not** secretly control unrelated components.
- The decision engine consumes explicit inputs from fusion, CV, ML, and sensors.

## ML Separation

```text
Dataset
   ↓
Training        (offline / separate pipeline)
   ↓
Evaluation
   ↓
Model Registry / Version
   ↓
Inference       (ROS node — subscribe, preprocess, predict, publish)
   ↓
Prediction
```

The inference node must **not**:

- train models
- directly manipulate GPIO
- own database schema logic
- control the frontend

## Data Separation

```text
Raw Data
   ↓
Validated Data
   ↓
Processed Data
   ↓
Features
   ↓
Training Dataset
   ↓
Model
```

Never silently overwrite raw data.

## Hardware Abstraction

Application code interacts with interfaces, not device specifics:

```python
sensor.read()   # not direct BME280 register reads in business logic
gpio.set_pin()  # not hard-coded Raspberry Pi calls in decision engine
```

All automated testing must work without physical hardware via `MockGPIO`, `VirtualSensor`, and simulated camera data.

## Related Docs

- [HARDWARE_ABSTRACTION.md](./HARDWARE_ABSTRACTION.md)
- [IRRIGATION_SAFETY.md](./IRRIGATION_SAFETY.md)
- [ML_PIPELINE.md](./ML_PIPELINE.md)
