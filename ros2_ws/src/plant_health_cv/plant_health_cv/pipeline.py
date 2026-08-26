"""
OpenCV processing stages for plant images.

Each public function documents *why* the algorithm is used (see also
docs/design/CV_ALGORITHMS.md). Prefer reading that doc over cargo-culting cv2 calls.
"""

from __future__ import annotations

import cv2
import numpy as np
import numpy.typing as npt

from plant_health_cv.result import BoundingBox, PipelineResult


def validate_bgr(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be ndarray")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"expected BGR HxWx3, got shape {image.shape}")
    if image.dtype != np.uint8:
        raise ValueError(f"expected uint8, got {image.dtype}")
    if image.size == 0:
        raise ValueError("empty image")
    return image


def resize_bgr(
    image: npt.NDArray[np.uint8],
    *,
    width: int,
    height: int,
) -> npt.NDArray[np.uint8]:
    """
    Algorithm: bilinear resize (cv2.INTER_LINEAR).

    Why: normalize resolution for stable HSV thresholds and feature scales.
    """
    if width < 8 or height < 8:
        raise ValueError("width/height must be >= 8")
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)


def denoise_bgr(image: npt.NDArray[np.uint8], *, ksize: int = 5) -> npt.NDArray[np.uint8]:
    """
    Algorithm: Gaussian blur.

    Why: reduce sensor noise before color thresholding; small ksize keeps edges.
    Sensitivity: larger ksize merges leaf boundaries; keep odd and small (3–7).
    """
    if ksize % 2 == 0 or ksize < 1:
        raise ValueError("ksize must be odd and >= 1")
    return cv2.GaussianBlur(image, (ksize, ksize), 0)


def bgr_to_hsv(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Algorithm: BGR→HSV color-space conversion.

    Why: plant green is more separable in Hue than in RGB under stable lighting.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def segment_green_hsv(
    hsv: npt.NDArray[np.uint8],
    *,
    h_min: int = 35,
    h_max: int = 85,
    s_min: int = 40,
    v_min: int = 40,
) -> npt.NDArray[np.uint8]:
    """
    Algorithm: HSV in-range threshold for green foliage.

    Why: controlled greenhouse lighting makes color segmentation practical
    before investing in deep-learning segmentation (see ADR candidates).
    Limitations: fails under strong yellow cast / mixed artificial lights.
    """
    lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper = np.array([h_max, 255, 255], dtype=np.uint8)
    return cv2.inRange(hsv, lower, upper)


def morph_cleanup(
    mask: npt.NDArray[np.uint8],
    *,
    open_ksize: int = 3,
    close_ksize: int = 5,
) -> npt.NDArray[np.uint8]:
    """
    Algorithm: morphological open then close.

    Why: open removes speckles; close fills small holes in leaf masks.
    """
    if open_ksize > 1:
        kernel_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_ksize, open_ksize))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_o)
    if close_ksize > 1:
        kernel_c = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_c)
    return mask


def largest_contour_roi(
    mask: npt.NDArray[np.uint8],
    bgr: npt.NDArray[np.uint8],
) -> tuple[npt.NDArray[np.uint8] | None, BoundingBox | None, float, tuple[float, float] | None]:
    """
    Algorithm: external contours; keep largest by area; crop bounding rect.

    Why: focus features on the primary plant region; ignore background clutter.
    Returns: (roi_bgr, bbox, contour_area, centroid_xy)
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None, 0.0, None
    largest = max(contours, key=cv2.contourArea)
    area = float(cv2.contourArea(largest))
    if area <= 0:
        return None, None, 0.0, None
    x, y, w, h = cv2.boundingRect(largest)
    roi = bgr[y : y + h, x : x + w].copy()
    moments = cv2.moments(largest)
    if moments["m00"] != 0:
        cx = float(moments["m10"] / moments["m00"])
        cy = float(moments["m01"] / moments["m00"])
        centroid = (cx, cy)
    else:
        centroid = None
    return roi, BoundingBox(x=x, y=y, width=w, height=h), area, centroid


def extract_mask_features(
    bgr: npt.NDArray[np.uint8],
    mask: npt.NDArray[np.uint8],
    *,
    contour_area: float,
    bbox: BoundingBox | None,
    centroid: tuple[float, float] | None,
) -> dict[str, float]:
    """Compute classical features used later by health/ML stages."""
    total = float(mask.size)
    leaf_pixels = float(np.count_nonzero(mask))
    green_ratio = leaf_pixels / total if total else 0.0
    hsv = bgr_to_hsv(bgr)
    if leaf_pixels > 0:
        mean_h, mean_s, mean_v, _ = cv2.mean(hsv, mask=mask)
    else:
        mean_h = mean_s = mean_v = 0.0
    features: dict[str, float] = {
        "leaf_area": leaf_pixels,
        "green_pixel_ratio": green_ratio,
        "mean_hue": float(mean_h),
        "mean_saturation": float(mean_s),
        "mean_value": float(mean_v),
        "contour_area": float(contour_area),
    }
    if bbox is not None:
        features["bbox_x"] = float(bbox.x)
        features["bbox_y"] = float(bbox.y)
        features["bbox_w"] = float(bbox.width)
        features["bbox_h"] = float(bbox.height)
    if centroid is not None:
        features["centroid_x"] = float(centroid[0])
        features["centroid_y"] = float(centroid[1])
    return features


def draw_visualization(
    bgr: npt.NDArray[np.uint8],
    mask: npt.NDArray[np.uint8],
    bbox: BoundingBox | None,
) -> npt.NDArray[np.uint8]:
    """Overlay mask edges and bbox for operator debugging."""
    viz = bgr.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(viz, contours, -1, (0, 255, 255), 2)
    if bbox is not None:
        cv2.rectangle(
            viz,
            (bbox.x, bbox.y),
            (bbox.x + bbox.width, bbox.y + bbox.height),
            (255, 128, 0),
            2,
        )
    return viz


def run_pipeline(
    image_bgr: npt.NDArray[np.uint8],
    *,
    width: int = 320,
    height: int = 240,
    blur_ksize: int = 5,
    h_min: int = 35,
    h_max: int = 85,
    s_min: int = 40,
    v_min: int = 40,
) -> PipelineResult:
    """Full PHP-06 pipeline: validate → resize → denoise → HSV → segment → ROI → features → viz."""
    image = validate_bgr(image_bgr)
    resized = resize_bgr(image, width=width, height=height)
    denoised = denoise_bgr(resized, ksize=blur_ksize)
    hsv = bgr_to_hsv(denoised)
    mask = segment_green_hsv(hsv, h_min=h_min, h_max=h_max, s_min=s_min, v_min=v_min)
    mask = morph_cleanup(mask)
    roi, bbox, contour_area, centroid = largest_contour_roi(mask, denoised)
    features = extract_mask_features(
        denoised, mask, contour_area=contour_area, bbox=bbox, centroid=centroid
    )
    viz = draw_visualization(denoised, mask, bbox)
    return PipelineResult(
        processed_bgr=denoised,
        mask=mask,
        roi_bgr=roi,
        viz_bgr=viz,
        features=features,
        bbox=bbox,
    )
