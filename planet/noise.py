"""Vectorised 3D gradient ("Perlin") noise and fractal sums of it.

We sample noise at each cell's (x, y, z) position on the unit sphere rather
than at (lat, lon). Sampling in 3D means there's no seam at the dateline
and no pinching at the poles, a classic beginner pitfall with 2D noise.
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange


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


@njit(parallel=True, cache=True)
def _fbm(pts, perm, grads, octaves, freq, lacunarity, gain, out):
    """fbm's octave sum, one pass per point (no (n, 3) temporaries per octave and corner). Perlin3D.__call__'s
    arithmetic in its order, so the values are bit-identical to the numpy version."""
    for i in prange(pts.shape[0]):
        total = 0.0
        amp, norm, fr = 1.0, 0.0, freq
        for o in range(octaves):
            sh = o * 17.31
            q0, q1, q2 = pts[i, 0] * fr + sh, pts[i, 1] * fr + sh, pts[i, 2] * fr + sh
            x0, y0, z0 = np.int64(np.floor(q0)), np.int64(np.floor(q1)), np.int64(np.floor(q2))
            f0, f1, f2 = q0 - x0, q1 - y0, q2 - z0
            u0 = f0 * f0 * f0 * (f0 * (f0 * 6 - 15) + 10)
            u1 = f1 * f1 * f1 * (f1 * (f1 * 6 - 15) + 10)
            u2 = f2 * f2 * f2 * (f2 * (f2 * 6 - 15) + 10)
            val = 0.0
            for dx in range(2):
                for dy in range(2):
                    for dz in range(2):
                        h = perm[perm[perm[(x0 + dx) & 255] + ((y0 + dy) & 255)] + ((z0 + dz) & 255)]
                        d0, d1, d2 = f0 - dx, f1 - dy, f2 - dz
                        dot = (grads[h, 0] * d0 + grads[h, 1] * d1) + grads[h, 2] * d2
                        w = (u0 if dx else 1 - u0) * (u1 if dy else 1 - u1) * (u2 if dz else 1 - u2)
                        val = val + w * dot
            total += amp * (val * 1.6)
            norm += amp
            fr *= lacunarity
            amp *= gain
        out[i] = total / norm


def fbm(noise: Perlin3D, pts: np.ndarray, octaves: int = 6, freq: float = 1.5,
        lacunarity: float = 2.0, gain: float = 0.5) -> np.ndarray:
    """Fractal Brownian motion: the same noise stacked at doubling frequencies
    and halving amplitudes. Big blobs + medium detail + fine detail."""
    if isinstance(noise, Perlin3D) and pts.ndim == 2 and pts.shape[1] == 3:
        out = np.empty(len(pts))
        _fbm(np.ascontiguousarray(pts, dtype=np.float64), noise.perm, noise.grads, octaves, float(freq),
             float(lacunarity), float(gain), out)
        return out
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
