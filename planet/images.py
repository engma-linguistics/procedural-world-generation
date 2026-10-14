"""Minimal PNG writer (no image library needed)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


def write_png(path: Path, img: np.ndarray) -> None:
    """Minimal PNG writer: (h, w, 3) uint8 RGB, or (h, w) uint16 greyscale."""
    if img.dtype == np.uint16 and img.ndim == 2:
        hgt, wid = img.shape
        raw = img.astype(">u2").view(np.uint8).reshape(hgt, wid * 2)
        ihdr = struct.pack(">IIBBBBB", wid, hgt, 16, 0, 0, 0, 0)
    elif img.dtype == np.uint8 and img.ndim == 3 and img.shape[2] == 3:
        hgt, wid = img.shape[:2]
        raw = img.reshape(hgt, wid * 3)
        ihdr = struct.pack(">IIBBBBB", wid, hgt, 8, 2, 0, 0, 0)
    else:
        raise ValueError(f"unsupported image {img.dtype} {img.shape}")
    data = np.concatenate([np.zeros((hgt, 1), np.uint8), raw], axis=1).tobytes()

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                           + chunk(b"IDAT", zlib.compress(data, 6)) + chunk(b"IEND", b""))
