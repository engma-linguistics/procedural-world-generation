"""Vectorised 3D gradient ("Perlin") noise and fractal sums of it.

We sample noise at each cell's (x, y, z) position on the unit sphere rather
than at (lat, lon). Sampling in 3D means there's no seam at the dateline
and no pinching at the poles, a classic beginner pitfall with 2D noise.
"""

from __future__ import annotations

import numpy as np


class Perlin3D:
    def __init__(self, seed: int):
        rng = np.random.default_rng(seed)
        perm = rng.permutation(256)
        self.perm = np.concatenate([perm, perm])
        g = rng.normal(size=(256, 3))
        self.grads = g / np.linalg.norm(g, axis=1, keepdims=True)

    def _hash(self, x, y, z):
        p = self.perm
        return p[p[p[x & 255] + (y & 255)] + (z & 255)]

    def __call__(self, pts: np.ndarray) -> np.ndarray:
        """pts: (N, 3). Returns values in roughly [-1, 1]."""
        p0 = np.floor(pts).astype(np.int64)
        f = pts - p0
        u = f * f * f * (f * (f * 6 - 15) + 10)  # smootherstep fade
        out = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    h = self._hash(p0[:, 0] + dx, p0[:, 1] + dy, p0[:, 2] + dz)
                    d = f - np.array([dx, dy, dz])
                    dot = (self.grads[h] * d).sum(axis=1)
                    w = (
                        (u[:, 0] if dx else 1 - u[:, 0])
                        * (u[:, 1] if dy else 1 - u[:, 1])
                        * (u[:, 2] if dz else 1 - u[:, 2])
                    )
                    out = out + w * dot
        return out * 1.6


def fbm(noise: Perlin3D, pts: np.ndarray, octaves: int = 6, freq: float = 1.5,
        lacunarity: float = 2.0, gain: float = 0.5) -> np.ndarray:
    """Fractal Brownian motion: the same noise stacked at doubling frequencies
    and halving amplitudes. Big blobs + medium detail + fine detail."""
    total = np.zeros(len(pts))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        # Offset each octave so they don't all line up at the origin.
        total += amp * noise(pts * freq + o * 17.31)
        norm += amp
        freq *= lacunarity
        amp *= gain
    return total / norm


def ridged(noise: Perlin3D, pts: np.ndarray, octaves: int = 5, freq: float = 2.0) -> np.ndarray:
    """Ridged multifractal: 1 - |noise| makes sharp crests, good for mountains."""
    total = np.zeros(len(pts))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        total += amp * (1 - np.abs(noise(pts * freq + o * 31.7))) ** 2
        norm += amp
        freq *= 2.0
        amp *= 0.5
    return total / norm
