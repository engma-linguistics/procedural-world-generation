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


def editor_schema() -> dict:
    """GET /api/lineage-schema: the peoples editor's option lists and defaults, from spec.py, land.GOODS and dragon_ages
    (viewer/lineages.html renders its menus from it, so they can't drift from what a tree may say; PW-1033)."""
    from . import dragon_ages as DA
    return {
        "traits": list(SP.TRAITS), "places": list(SP.PLACES), "groups": list(SP.GROUPS), "ways": list(SP.WAYS),
        "realms": list(SP.REALMS), "goods": {k: label for k, (label, _) in LD.GOODS.items()},
        "pair_wants": list(SP.PAIR_WANTS), "stages": list(SP.STAGES), "stage_notes": SP.STAGE_NOTES,
        "band": SP.BAND, "demo_default": SP.DEMO_DEFAULT, "demography": SP.DEMOGRAPHY,
        "body_default": SP.BODY_DEFAULT, "body_choices": {k: list(v) for k, v in SP.BODY_CHOICES.items()},
        "body_bools": [k for k, v in SP.BODY_DEFAULT.items() if isinstance(v, bool)], "toxins": list(SP.TOXINS),
        "eras": list(SP.ERAS), "modes": list(SP.MODES), "portal_modes": list(SP.PORTAL_MODES),
        "megafauna_natural": [[k, SP.MEGAFAUNA_NATURAL_LABELS[k]] for k in SP.MEGAFAUNA_NATURAL],
        "dragon_ages": list(DA.SCHEDULES), "dragon_generation": list(DA.GENERATION),
        "defaults": {"era": SP.ERA_DEFAULT, "mode": SP.MODE_DEFAULT, "portal_mode": SP.Tree.portal_mode,
                     "megafauna_natural": SP.MEGAFAUNA_NATURAL_DEFAULT, "dragon_ages": DA.DEFAULT,
                     "dragon_generation": DA.GENERATION_DEFAULT, "dragon_km2": SP.DRAGON_KM2, "giant_km2": SP.GIANT_KM2,
                     "press_early": 1.0, "press_late": 1.0, "press_x": list(SP.PRESS_X), "forager_km2": SP.FORAGER_KM2, "viable_pop": SP.VIABLE_POP, "land_pull": SP.LAND_PULL},
    }


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


def load_tree(ref: str, mode: str | None = None) -> SP.Tree:
    p = Path(ref)
    if p.is_file():
        return SP.load(p, mode)
    return SP.load(tree_path(ref), mode)


def run(ref: str, tree: SP.Tree, tries: int = 4, now: float | None = None, recent_kyr: float = 30.0,
        name: str | None = None, progress=lambda f, msg: None, climate_every: float = 2.0) -> Path:
    tz, now0, world = R.resolve(ref)
    ps = R.Pass(tz, now0 if now is None else now, R.RecentParams(kyr=recent_kyr, climate_every=climate_every), world_ref=world)
    goods = None
    if world and tree.uses:
        progress(0.0, "the land's goods (game attributes, resources, coasts)")
        goods = LD.goods(world)
        if tree.mode == "real" and goods:  # (no fantasy goods in the real world)
            goods = {k: v for k, v in goods.items() if k not in SP.FANTASY_GOODS}
    h, res, pres = simulate(tree, ps, tries, progress, goods=goods)
    return save(h, res, pres, world=world, name=name)


def job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/lineages {world | timezoom, tree (name) | raw (the tree itself), tries}."""
    ref = req.get("world") or req.get("timezoom")
    if not ref:
        raise ValueError("give world or timezoom")
    tree = SP.parse(req["raw"], req.get("mode")) if req.get("raw") else load_tree(req["tree"], req.get("mode"))
    if req.get("tree"):
        tree.source = req["tree"]
    out = run(str(ref).removesuffix(".json"), tree, int(req.get("tries", 4)), progress=progress)
    return {"run": out.name}
