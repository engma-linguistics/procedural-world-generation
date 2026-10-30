"""Minimal PNG writer (no image library needed) and small colour helpers."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


def write_png(path: Path, img: np.ndarray) -> None:
    """Minimal PNG writer: (h, w, 3) uint8 RGB, (h, w, 4) uint8 RGBA, (h, w)
    uint8 or uint16 greyscale."""
    if img.dtype == np.uint16 and img.ndim == 2:
        hgt, wid = img.shape
        raw = img.astype(">u2").view(np.uint8).reshape(hgt, wid * 2)
        ihdr = struct.pack(">IIBBBBB", wid, hgt, 16, 0, 0, 0, 0)
    elif img.dtype == np.uint8 and img.ndim == 3 and img.shape[2] in (3, 4):
        hgt, wid, ch = img.shape
        raw = img.reshape(hgt, wid * ch)
        ihdr = struct.pack(">IIBBBBB", wid, hgt, 8, 2 if ch == 3 else 6, 0, 0, 0)
    elif img.dtype == np.uint8 and img.ndim == 2:
        hgt, wid = img.shape
        raw = img
        ihdr = struct.pack(">IIBBBBB", wid, hgt, 8, 0, 0, 0, 0)
    else:
        raise ValueError(f"unsupported image {img.dtype} {img.shape}")
    data = np.concatenate([np.zeros((hgt, 1), np.uint8), raw], axis=1).tobytes()

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                           + chunk(b"IDAT", zlib.compress(data, 6)) + chunk(b"IEND", b""))


def hex_rgb(c: str) -> tuple:
    """'#rrggbb' -> (r, g, b) as 0..255 ints."""
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def ramp_colour(v, stops) -> np.ndarray:
    """Piecewise-linear colour (..., 3) of values v through [(value, (r, g, b)), ...]."""
    xs = np.array([s[0] for s in stops], float)
    cols = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(v, xs, cols[:, k]) for k in range(3)], -1)
