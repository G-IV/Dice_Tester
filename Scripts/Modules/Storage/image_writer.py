from datetime import datetime
from pathlib import Path
import re

import cv2


def _safe_token(value: str) -> str:
    """Return a filesystem-safe token for use in filenames."""
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return token or "unknown"


def write_frame_image(
    frame,
    output_dir: Path,
    dice_id: str | None = None,
    dice_value: str | None = None,
    dice_sides: int | None = None,
) -> str:
    """Write a frame to disk and return the absolute file path as a string."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename_parts = [timestamp]

    if dice_id:
        filename_parts.append(f"die-{_safe_token(str(dice_id))}")
    if dice_value:
        filename_parts.append(f"val-{_safe_token(str(dice_value))}")
    if dice_sides is not None:
        filename_parts.append(f"sides-{_safe_token(str(dice_sides))}")

    filename = "__".join(filename_parts) + ".jpg"
    image_path = output_dir / filename

    if not cv2.imwrite(str(image_path), frame):
        raise RuntimeError(f"Failed to write image to {image_path}")

    return str(image_path)
