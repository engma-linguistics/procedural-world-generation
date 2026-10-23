"""Entry points: the CLI (`planet lineages`) and the server (`POST /api/lineages`)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .. import store as S
from . import recent as R
from . import land as LD
from . import spec as SP
from .history import simulate
from .output import save

SAMPLES = Path(__file__).parent / "samples"
_NAME = re.compile(r"^[0-9A-Za-z_-]{1,64}$")


def trees_dir() -> Path:
    return S.root() / "lineage_trees"


def list_trees() -> list[dict]:
    """The presets (samples/) and the saved trees (<data>/lineage_trees/)."""
    out = [{"name": p.stem, "kind": "preset", "file": str(p)} for p in sorted(SAMPLES.glob("*.toml"))]
    d = trees_dir()
    if d.is_dir():
        out += [{"name": p.stem, "kind": "saved", "file": str(p)} for p in sorted(d.glob("*.json"))]
    return out


def tree_path(name: str) -> Path:
    if not _NAME.match(name or ""):
        raise ValueError("a tree name is letters, digits, - and _")
    for t in list_trees()[::-1]:  # (a saved tree shadows a preset of the same name)
        if t["name"] == name:
            return Path(t["file"])
    raise FileNotFoundError(f"no tree {name!r}")


def read_raw(name: str) -> dict:
    import tomllib
    p = tree_path(name)
    return json.loads(p.read_text()) if p.suffix == ".json" else tomllib.loads(p.read_text())


def save_raw(name: str, raw: dict) -> Path:
    """Validate and save an edited tree as <data>/lineage_trees/<name>.json."""
    if not _NAME.match(name or ""):
        raise ValueError("a tree name is letters, digits, - and _")
    SP.parse(raw)  # (raises ValueError with the problem)
    d = trees_dir()
    d.mkdir(parents=True, exist_ok=True)
    return S.write_atomic(d / f"{name}.json", json.dumps(raw, indent=1))


def load_tree(ref: str) -> SP.Tree:
    p = Path(ref)
    if p.is_file():
        return SP.load(p)
    return SP.load(tree_path(ref))


def run(ref: str, tree: SP.Tree, tries: int = 4, now: float | None = None, recent_kyr: float = 30.0,
        name: str | None = None, progress=lambda f, msg: None) -> Path:
    tz, now0, world = R.resolve(ref)
    ps = R.Pass(tz, now0 if now is None else now, R.RecentParams(kyr=recent_kyr), world_ref=world)
    goods = None
    if world and tree.uses:
        progress(0.0, "the land's goods (game attributes, resources, coasts)")
        goods = LD.goods(world)
    h, res, pres = simulate(tree, ps, tries, progress, goods=goods)
    return save(h, res, pres, world=world, name=name)


def job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/lineages {world | timezoom, tree (name) | raw (the tree itself), tries}."""
    ref = req.get("world") or req.get("timezoom")
    if not ref:
        raise ValueError("give world or timezoom")
    tree = SP.parse(req["raw"]) if req.get("raw") else load_tree(req["tree"])
    if req.get("tree"):
        tree.source = req["tree"]
    out = run(str(ref).removesuffix(".json"), tree, int(req.get("tries", 4)), progress=progress)
    return {"run": out.name}
