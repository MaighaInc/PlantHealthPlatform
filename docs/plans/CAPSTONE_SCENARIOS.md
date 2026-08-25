# Capstone Test Scenarios

> Acceptance scenarios for Plant Health System (PHS) — validate at PHP-30

---

## Scenario 1 — Healthy Plant

**Input:**

```text
normal soil
normal environment
healthy image
```

**Expected:**

```text
health = healthy
irrigation = OFF
```

---

## Scenario 2 — Dry Soil

**Input:**

```text
soil = dry
```

**Expected:**

```text
health = stressed
decision = irrigation required
```

(Safety layer must still validate before actuation.)

---

## Scenario 3 — Invalid Sensor

**Input:**

```text
soil sensor = invalid
```

**Expected:**

```text
sensor = INVALID
irrigation = BLOCKED
alert = GENERATED
```

---

## Scenario 4 — Low ML Confidence

**Input:**

```text
ML confidence < configured threshold
```

**Expected:**

```text
prediction = UNKNOWN
automatic irrigation based solely on ML = BLOCKED
```

---

## Scenario 5 — Manual Irrigation

**Input:**

```text
authorized manual command
```

**Expected:**

```text
authorization
   ↓
safety validation
   ↓
relay ON
   ↓
event recorded
   ↓
maximum duration enforced
   ↓
relay OFF
```

---

## Full E2E Pipeline (PHP-29 / PHP-30)

```text
Camera → ROS 2 → OpenCV → Features → ML → Health Engine → Sensor Fusion
  → Decision Engine → Safety Layer → GPIO (mock or real)
        +
Backend → PostgreSQL → REST API → React Dashboard
```

## Related Docs

- [ROADMAP.md](./ROADMAP.md)
- [../design/IRRIGATION_SAFETY.md](../design/IRRIGATION_SAFETY.md)
- [../development/TESTING.md](../development/TESTING.md)
