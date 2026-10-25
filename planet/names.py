"""Names for a world's landmasses (PW-853): pronounceable, deterministic from the world's seed and the landmass's rank by area.

The same pair always gives the same name, so the world's summary (stored with the world, shown in the viewer) and the peoples' history
(lineages: crossings, discoveries) agree without either having to pass the other a list. The largest landmass is rank 0.
"""
from __future__ import annotations

import zlib

import numpy as np

ONSETS = ("b", "d", "g", "h", "j", "k", "l", "m", "n", "r", "s", "t", "v", "z", "br", "dr", "th", "sh", "tr", "kh")
VOWELS = ("a", "e", "i", "o", "u", "a", "o", "a")
CODAS = ("", "", "", "n", "r", "l", "s", "m", "th")  # (the last syllable only)


def landmass_name(seed, rank: int, taken: tuple[str, ...] = ()) -> str:
    """The name of the landmass of this rank (0: the largest) in the world with this seed (an int or a string). `taken`: names to avoid
    (the rest of the same world's list); a clash draws again from the same stream, so the result is still a function of its inputs."""
    key = zlib.crc32(str(seed).encode())
    rng = np.random.default_rng((key, 853, int(rank)))
    for _ in range(40):
        n = int(rng.integers(2, 4))  # two or three open syllables, the last one maybe closed
        parts = [ONSETS[int(rng.integers(len(ONSETS)))] + VOWELS[int(rng.integers(len(VOWELS)))] for _ in range(n)]
        name = ("".join(parts) + CODAS[int(rng.integers(len(CODAS)))]).capitalize()
        if name not in taken:
            return name
    return name


def landmass_names(seed, count: int) -> list[str]:
    """Names for ranks 0..count-1, all different."""
    out: list[str] = []
    for r in range(count):
        out.append(landmass_name(seed, r, tuple(out)))
    return out
