# CV Algorithms Used in PHP-06

> Learning requirement: every important `cv2` call is justified here.

---

## 1. Bilinear resize (`cv2.resize`, `INTER_LINEAR`)

| Field | Content |
|-------|---------|
| **Problem** | Cameras publish varying resolutions; thresholds and features need stable scale. |
| **Algorithm** | Bilinear interpolation resize to configured `process_width` × `process_height`. |
| **Why** | Cheap, good quality for downscaling before segmentation. |
| **Parameters** | `process_width`, `process_height` (default 320×240). |
| **Sensitivity** | Too small → lost leaf detail; too large → slower pipeline. |
| **Limitations** | Upscaling does not invent detail. |
| **Alternatives** | `INTER_AREA` for strong downscale; letterbox keep-aspect later. |
| **Tradeoffs** | Fixed size distorts aspect ratio slightly — acceptable for early milestones. |

---

## 2. Gaussian blur (`cv2.GaussianBlur`)

| Field | Content |
|-------|---------|
| **Problem** | Sensor noise creates speckles that break HSV thresholds. |
| **Algorithm** | Separable Gaussian smoothing with odd kernel size. |
| **Why** | Simple, fast denoise before color segmentation. |
| **Parameters** | `blur_ksize` (default 5, must be odd). |
| **Sensitivity** | Large ksize erodes thin leaves and merges nearby objects. |
| **Limitations** | Does not remove motion blur. |
| **Alternatives** | Bilateral filter (edge-preserving, slower); median blur for salt-pepper. |
| **Tradeoffs** | Blur vs edge fidelity. |

---

## 3. BGR → HSV (`cv2.cvtColor`)

| Field | Content |
|-------|---------|
| **Problem** | Green foliage is hard to isolate in RGB under lighting changes. |
| **Algorithm** | Convert to HSV; segment primarily on Hue + Saturation/Value floors. |
| **Why** | Hue is more lighting-stable for green plants in controlled settings. |
| **Parameters** | Implicit OpenCV conversion. |
| **Sensitivity** | OpenCV Hue is 0–179 (not 0–360). |
| **Limitations** | Strong colored artificial light shifts Hue. |
| **Alternatives** | Lab/`a*` channel; learned segmentation (later). |
| **Tradeoffs** | Classical HSV is explainable and cheap vs CNN segmentation. |

---

## 4. HSV in-range segmentation (`cv2.inRange`)

| Field | Content |
|-------|---------|
| **Problem** | Separate plant pixels from soil/background. |
| **Algorithm** | Threshold Hue∈[`h_min`,`h_max`], S≥`s_min`, V≥`v_min`. |
| **Why** | Greenhouse lighting makes color gates practical (ADR candidate vs DL). |
| **Parameters** | `h_min=35`, `h_max=85`, `s_min=40`, `v_min=40` (tunable). |
| **Sensitivity** | Yellow-green leaves need wider H; dark leaves need lower `v_min`. |
| **Limitations** | Brown diseased tissue may fall outside green band (OK — not “leaf green”). |
| **Alternatives** | GrabCut; deep segmentation. |
| **Tradeoffs** | Brittle outdoors; fine for SIMULATION + early lab. |

---

## 5. Morphology open/close (`cv2.morphologyEx`)

| Field | Content |
|-------|---------|
| **Problem** | Mask speckles and holes confuse contour/ROI. |
| **Algorithm** | Open (remove dots) then close (fill gaps) with elliptical kernels. |
| **Why** | Classical cleanup matched to blob-like leaves. |
| **Parameters** | open 3×3, close 5×5 (code defaults). |
| **Sensitivity** | Large close kernel can bridge plant to background clutter. |
| **Limitations** | Cannot recover missing large regions. |
| **Alternatives** | Contour area filter only; CRF post-process. |
| **Tradeoffs** | Cleaner mask vs shape distortion. |

---

## 6. Largest external contour + bbox (`findContours`, `boundingRect`, moments)

| Field | Content |
|-------|---------|
| **Problem** | Need a primary plant ROI for features and visualization. |
| **Algorithm** | External contours; maximize `contourArea`; crop bbox; centroid via moments. |
| **Why** | Single dominant plant assumption fits early PHS demos. |
| **Parameters** | None beyond mask quality. |
| **Sensitivity** | Two plants → may pick the larger only. |
| **Limitations** | No instance segmentation of multiple plants. |
| **Alternatives** | Watershed; detector network. |
| **Tradeoffs** | Simplicity now; multi-plant later. |

---

## Related

- Pipeline code: `ros2_ws/src/plant_health_cv/plant_health_cv/pipeline.py`
- Overview: [CV_PIPELINE.md](./CV_PIPELINE.md)
