"""Utility for compositing an info panel to the left of a rendered frame."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np


_PANEL_WIDTH = 560
_FONT = cv2.FONT_HERSHEY_DUPLEX
_FONT_SCALE_HEADER = 1.17
_FONT_SCALE_BODY = 0.99
_FONT_THICKNESS = 1
_LINE_HEIGHT = 44
_SECTION_GAP = 14
_MARGIN_LEFT = 14
_MARGIN_TOP = 28
_BG_COLOR = (30, 30, 30)        # dark grey background
_HEADER_COLOR = (180, 180, 255)  # soft blue-white for section headers
_TEXT_COLOR = (220, 220, 220)    # light grey for body text
_VALUE_COLOR = (100, 240, 100)   # green for data values
_NA_COLOR = (130, 130, 130)      # muted grey for N/A values


@dataclass
class FrameContext:
    """All context that may be available for a given frame.  Every field is optional."""
    # Live analysis fields
    dice_state: str | None = None       # e.g. 'SETTLED', 'MOVING', 'UNKNOWN'
    dice_value: int | str | None = None  # detected face value
    roll_number: int | None = None       # submitted samples so far
    target_samples: int | None = None    # total target
    eta_text: str | None = None          # estimated time remaining for live capture
    dice_id: str | None = None
    dice_sides: int | None = None
    # Historical stats (populated from DB rows)
    total_rolls: int | None = None
    mean_roll: float | None = None
    expected_mean: float | None = None
    # Per-face frequency map {face_value: count}
    face_counts: dict[int, int] = field(default_factory=dict)
    # Browse-mode fields (from YOLO result)
    detections: list[dict[str, Any]] = field(default_factory=list)
    # File context (browse mode)
    image_index: int | None = None
    image_total: int | None = None
    image_name: str | None = None
    # Video frame info
    frame_number: int | None = None
    frame_total: int | None = None
    # Indicates whether frame content is linked to DB-backed dice history
    db_linked: bool | None = None


def _na(value: Any, fmt: str = '{}') -> tuple[str, tuple[int, int, int]]:
    """Return (text, color) — green value or muted N/A."""
    if value is None:
        return 'N/A', _NA_COLOR
    return fmt.format(value), _VALUE_COLOR


def _draw_row(img: np.ndarray, y: int, label: str, value: Any, fmt: str = '{}') -> int:
    val_text, val_color = _na(value, fmt)
    label_text = f'{label}:'
    cv2.putText(img, label_text, (_MARGIN_LEFT, y), _FONT, _FONT_SCALE_BODY, _TEXT_COLOR, _FONT_THICKNESS, cv2.LINE_AA)
    cv2.putText(img, val_text, (_MARGIN_LEFT + 290, y), _FONT, _FONT_SCALE_BODY, val_color, _FONT_THICKNESS, cv2.LINE_AA)
    return y + _LINE_HEIGHT


def _draw_header(img: np.ndarray, y: int, text: str) -> int:
    cv2.putText(img, text, (_MARGIN_LEFT, y), _FONT, _FONT_SCALE_HEADER, _HEADER_COLOR, _FONT_THICKNESS, cv2.LINE_AA)
    cv2.line(img, (_MARGIN_LEFT, y + 3), (_PANEL_WIDTH - _MARGIN_LEFT, y + 3), _HEADER_COLOR, 1)
    return y + _LINE_HEIGHT + 2


def build_info_panel(height: int, ctx: FrameContext) -> np.ndarray:
    """Return a (_PANEL_WIDTH x height) BGR image containing the info panel."""
    panel = np.full((height, _PANEL_WIDTH, 3), _BG_COLOR, dtype=np.uint8)
    y = _MARGIN_TOP

    # --- Current frame / dice state ---
    y = _draw_header(panel, y, 'CURRENT FRAME')

    if ctx.dice_state is not None or ctx.dice_value is not None or ctx.roll_number is not None:
        y = _draw_row(panel, y, 'State', ctx.dice_state)
        y = _draw_row(panel, y, 'Value', ctx.dice_value)
        if ctx.roll_number is not None and ctx.target_samples is not None:
            y = _draw_row(panel, y, 'Roll', f'{ctx.roll_number}/{ctx.target_samples}')
        else:
            y = _draw_row(panel, y, 'Roll', ctx.roll_number)
    elif ctx.detections:
        # Browse mode — list detected objects
        for det in ctx.detections[:4]:
            name = det.get('name', '?')
            conf = det.get('conf')
            conf_str = f'{conf:.2f}' if conf is not None else 'N/A'
            y = _draw_row(panel, y, name, conf_str)
    else:
        y = _draw_row(panel, y, 'Detections', None)

    # Frame / position counter
    if ctx.frame_number is not None:
        y = _draw_row(panel, y, 'Frame', f'{ctx.frame_number}/{ctx.frame_total or "?"}')
    if ctx.image_index is not None:
        y = _draw_row(panel, y, 'Image', f'{ctx.image_index}/{ctx.image_total or "?"}')
    if ctx.image_name:
        # Truncate long names
        name = ctx.image_name if len(ctx.image_name) <= 30 else '...' + ctx.image_name[-27:]
        y = _draw_row(panel, y, 'File', name)
    if ctx.db_linked is not None:
        y = _draw_row(panel, y, 'DB linked', 'Yes' if ctx.db_linked else 'No')
    else:
        y = _draw_row(panel, y, 'DB linked', None)

    y += _SECTION_GAP

    # --- Dice identity ---
    y = _draw_header(panel, y, 'DICE INFO')
    y = _draw_row(panel, y, 'ID', ctx.dice_id)
    y = _draw_row(panel, y, 'Sides', ctx.dice_sides)

    y += _SECTION_GAP

    # --- Historical stats ---
    y = _draw_header(panel, y, 'HISTORICAL STATS')
    y = _draw_row(panel, y, 'Total rolls', ctx.total_rolls)
    y = _draw_row(panel, y, 'Mean roll', ctx.mean_roll, fmt='{:.2f}')
    y = _draw_row(panel, y, 'Expected mean', ctx.expected_mean, fmt='{:.2f}')

    # Per-face counts (compact)
    if ctx.face_counts and y + _LINE_HEIGHT * (len(ctx.face_counts) + 2) < height:
        y += _SECTION_GAP // 2
        y = _draw_header(panel, y, 'FACE COUNTS')
        for face in sorted(ctx.face_counts):
            y = _draw_row(panel, y, f'  Face {face}', ctx.face_counts[face])
            if y + _LINE_HEIGHT > height - 10:
                break

    # Live-mode ETA footer pinned to panel bottom.
    if ctx.target_samples is not None:
        footer_y = max(_MARGIN_TOP + _LINE_HEIGHT, height - 20)
        cv2.line(panel, (_MARGIN_LEFT, footer_y - 22), (_PANEL_WIDTH - _MARGIN_LEFT, footer_y - 22), _HEADER_COLOR, 1)
        eta_value = ctx.eta_text if ctx.eta_text is not None else 'Calculating...'
        _draw_row(panel, footer_y, 'ETA', eta_value)

    return panel


def composite_with_panel(frame: np.ndarray, ctx: FrameContext) -> np.ndarray:
    """Return a new image with the info panel prepended to the left of frame."""
    panel = build_info_panel(frame.shape[0], ctx)
    return np.concatenate([panel, frame], axis=1)
