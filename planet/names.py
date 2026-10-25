"""Names for a world's landmasses (PW-853): pronounceable, deterministic from the world's seed and the landmass's rank by area.

The same pair always gives the same name, so the world's summary (stored with the world, shown in the viewer) and the peoples' history
(lineages: crossings, discoveries) agree without either having to pass the other a list. The largest landmass is rank 0.
"""
from __future__ import annotations

import json
import zlib
from pathlib import Path

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


def rank_letter(rank: int) -> str:
    """A, B, ... Z, AA, ... for rank 0, 1, ...: the letter a landmass carries in the summary of a world made before PW-853, and the key
    an owner-given name is stored under (PW-867)."""
    s, i = "", int(rank) + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def landmass_names(seed, count: int, overrides: dict | None = None) -> list[str]:
    """Names for ranks 0..count-1, all different. `overrides` (letter -> name, load_overrides): the owner's own names for some ranks
    replace the generated ones (the rest keep theirs: a generated name never changes because another was overridden)."""
    out: list[str] = []
    for r in range(count):
        out.append(landmass_name(seed, r, tuple(out)))
    ov = overrides or {}
    return [ov.get(rank_letter(r), n) for r, n in enumerate(out)]


# -- the owner's names, kept beside the world (worlds/names/<id>.json: {"A": "Jangwa"}; planet name world:<id> A=Jangwa) -------------
def overrides_path(world_id: str) -> Path:
    from . import store as S
    return S.names_path(world_id)


def load_overrides(world_id: str | None) -> dict[str, str]:
    """The owner's names for this world's landmasses by letter ({} when there are none, or no world)."""
    if not world_id:
        return {}
    p = overrides_path(str(world_id))
    try:
        d = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    return {str(k).upper(): str(v) for k, v in d.items() if str(v).strip()} if isinstance(d, dict) else {}


def save_overrides(world_id: str, ov: dict[str, str]) -> Path:
    p = overrides_path(world_id)
    if not ov:
        p.unlink(missing_ok=True)
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({k: ov[k] for k in sorted(ov, key=lambda x: (len(x), x))}, indent=1, ensure_ascii=False) + "\n")
    return p


def world_landmasses(ref: str):
    """(world id, header, landmasses, generated names) of a saved world: the summary's landmasses by rank and the names the seed gives them
    (letters for a world without a seed). SystemExit when there is no such world."""
    from . import store as S
    ref = ref.split(":", 1)[-1]
    if not S.exists("world", ref):
        raise SystemExit(f"ERROR: no world {ref!r} (run planet list)")
    path = S.find_world(ref)
    head, summary = S.read_header(path, ("id", "name", "meta")), {}
    with open(path) as fh:  # (the summary is one line of the file, before the layers)
        for line in fh:
            if line.startswith('"summary": '):
                summary = json.loads(line[len('"summary": '):].rstrip().rstrip(","))
                break
            if line.startswith('"layers"'):
                break
    seed = head.get("meta", {}).get("seed")
    lms = summary.get("landmasses") or []
    lms = lms if isinstance(lms, list) else []
    gen = landmass_names(seed, len(lms)) if seed is not None else [rank_letter(i) for i in range(len(lms))]
    return path.stem, head, lms, gen


def set_name(ref: str, letter: str, name: str) -> list[dict]:
    """Give landmass `letter` of a world your own name (an empty name clears it back to the generated one); the file is the CLI's
    (worlds/names/<id>.json). Returns [{letter, name, generated, custom}] for the world's landmasses."""
    wid, _head, lms, gen = world_landmasses(ref)
    letter = str(letter).strip().upper()
    if not letter.isalpha() or letter not in {rank_letter(i) for i in range(len(lms))}:
        raise ValueError(f"{letter!r} is not a landmass of this world")
    ov = load_overrides(wid)
    name = " ".join(str(name).split())[:40]
    if name:
        ov[letter] = name
    else:
        ov.pop(letter, None)
    save_overrides(wid, ov)
    return [{"letter": rank_letter(i), "name": ov.get(rank_letter(i), g), "generated": g, "custom": rank_letter(i) in ov} for i, g in enumerate(gen)]
