# Computer Vision Pipeline

> OpenCV processing stages and learning requirements

## Recommended Pipeline

```text
Raw Image
   ↓
Image Validation
   ↓
Resize
   ↓
Noise Reduction
   ↓
Color Conversion
   ↓
Plant Segmentation
   ↓
ROI Extraction
   ↓
Feature Extraction
   ↓
Visualization
```

## Supported Capabilities (progressive)

- Image acquisition, validation, resizing
- Color-space conversion (HSV, etc.)
- HSV segmentation, thresholding
- Morphological operations
- Contour detection, shape analysis
- Leaf segmentation, background removal
- ROI extraction, feature extraction
- Normalization, augmentation
- Image quality assessment

## Potential Features

```text
leaf_area
green_pixel_ratio
mean_hue
mean_saturation
mean_value
contour_area
bounding_box
centroid
```

## Learning Requirement

For every important CV algorithm, document:

```text
Problem
Algorithm
Reason for selection
Parameters
Parameter sensitivity
Limitations
Alternatives
Tradeoffs
```

The intern must understand algorithms — do not allow unexplained `cv2.some_function(...)` usage.

## Camera Subsystem Requirements

- USB camera acquisition
- ROS image publishing via `cv_bridge`
- Configurable resolution and FPS
- Camera failure detection
- Timestamping, dropped/invalid frame detection
- Shutdown handling and resource release
- Reconnection where practical

## Related Docs

- [DATA_PIPELINE.md](./DATA_PIPELINE.md)
- [ML_PIPELINE.md](./ML_PIPELINE.md)
- [../plans/ROADMAP.md](../plans/ROADMAP.md) — PHP-05, PHP-06, PHP-07, PHP-10
