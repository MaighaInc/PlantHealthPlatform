"""CV node parameter validation (no rclpy)."""

from __future__ import annotations

from dataclasses import dataclass


class CvParameterError(ValueError):
    """Invalid CV ROS/runtime parameter."""


def _odd_ksize(name: str, value: int) -> int:
    iv = int(value)
    if iv < 1 or iv % 2 == 0:
        raise CvParameterError(f"{name} must be odd and >= 1, got {iv}")
    return iv


@dataclass(frozen=True)
class CvNodeParams:
    process_width: int
    process_height: int
    blur_ksize: int
    h_min: int
    h_max: int
    s_min: int
    v_min: int
    image_topic: str = "/camera/image_raw"
    processed_topic: str = "/camera/image_processed"
    roi_topic: str = "/plant/roi"

    @classmethod
    def from_raw(
        cls,
        *,
        process_width: int,
        process_height: int,
        blur_ksize: int,
        h_min: int,
        h_max: int,
        s_min: int,
        v_min: int,
        image_topic: str = "/camera/image_raw",
        processed_topic: str = "/camera/image_processed",
        roi_topic: str = "/plant/roi",
    ) -> CvNodeParams:
        if int(process_width) < 8 or int(process_height) < 8:
            raise CvParameterError("process_width/height must be >= 8")
        h0, h1 = int(h_min), int(h_max)
        if not (0 <= h0 <= h1 <= 179):
            raise CvParameterError(f"invalid hue range [{h0}, {h1}]")
        if not (0 <= int(s_min) <= 255 and 0 <= int(v_min) <= 255):
            raise CvParameterError("s_min/v_min must be in [0, 255]")
        for name, topic in (
            ("image_topic", image_topic),
            ("processed_topic", processed_topic),
            ("roi_topic", roi_topic),
        ):
            if not str(topic).startswith("/"):
                raise CvParameterError(f"{name} must be absolute, got {topic!r}")
        return cls(
            process_width=int(process_width),
            process_height=int(process_height),
            blur_ksize=_odd_ksize("blur_ksize", blur_ksize),
            h_min=h0,
            h_max=h1,
            s_min=int(s_min),
            v_min=int(v_min),
            image_topic=str(image_topic),
            processed_topic=str(processed_topic),
            roi_topic=str(roi_topic),
        )
