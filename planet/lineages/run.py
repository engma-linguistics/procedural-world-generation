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
    from . import ladder as LA
    from . import life_history as LH
    from . import ranges as RG
    return {
        "traits": list(SP.TRAITS), "places": list(SP.PLACES), "groups": list(SP.GROUPS), "ways": list(SP.WAYS),
        "realms": list(SP.REALMS), "goods": {k: label for k, (label, _) in LD.GOODS.items()},
        "pair_wants": list(SP.PAIR_WANTS), "stages": list(SP.STAGES), "stage_notes": SP.STAGE_NOTES,
        "band": SP.BAND, "demo_default": SP.DEMO_DEFAULT, "demography": SP.DEMOGRAPHY, "kind_range": list(SP.KIND_RANGE),
        "ladder": [list(r) for r in LA.TABLE], "ranges": RG.table(),  # (the published ranges a run's draws are shown against, PW-1401)
        "body_default": SP.BODY_DEFAULT, "body_choices": {k: list(v) for k, v in SP.BODY_CHOICES.items()},
        "body_bools": [k for k, v in SP.BODY_DEFAULT.items() if isinstance(v, bool)], "toxins": list(SP.TOXINS),
        "eras": list(SP.ERAS), "gods_modes": list(SP.GODS_MODES), "modes": list(SP.MODES), "portal_modes": list(SP.PORTAL_MODES),
        "megafauna_natural": [[k, SP.MEGAFAUNA_NATURAL_LABELS[k]] for k in SP.MEGAFAUNA_NATURAL],
        "dragon_ages": list(DA.SCHEDULES), "dragon_generation": list(DA.GENERATION),
        "defaults": {"era": SP.ERA_DEFAULT, "gods_mode": "faith_made", "mode": SP.MODE_DEFAULT, "portal_mode": SP.Tree.portal_mode,
                     "megafauna_natural": SP.MEGAFAUNA_NATURAL_DEFAULT, "dragon_ages": DA.DEFAULT,
                     "dragon_generation": DA.GENERATION_DEFAULT, "dragon_km2": SP.DRAGON_KM2, "giant_km2": SP.GIANT_KM2,
                     "press_early": 1.0, "press_late": 1.0, "press_x": list(SP.PRESS_X), "rivals": 1.0, "rivals_x": list(SP.RIVALS_X),
                     "dragon_abundance": 1.0, "abundance_x": list(SP.ABUNDANCE_X),
                     "game_share": 1.0, "game_share_x": list(SP.GAME_SHARE_X), "overkill": 0.6, "overkill_x": list(SP.OVERKILL_X),
                     "forager_km2": SP.FORAGER_KM2, "viable_pop": SP.VIABLE_POP, "land_pull": SP.LAND_PULL,
                     "surge_early": 1.0, "surge_late": 1.0, "raiders": 1.0, "war": 1.0,
                     "war_early": 1.0, "war_late": 1.0, "war_x": list(SP.WAR_X),  # (lane 259: war-torn land's era pair, PW-1172)
                     "brake_x": list(SP.BRAKE_X)},  # (lane 97: the raiders' brakes and war-torn land, meta.raiders / meta.war)
        "surge_x": list(SP.SURGE_X),  # (the momentum edge's dial per era, lane 73)
        "breeding": list(LH.BREEDING), "survival": list(LH.SURVIVAL), "life_stages": list(LH.STAGES),  # (lane 78: life history)
        "life_defaults": {"wave_kyr": SP.WAVE_KYR, "portal_open_kyr": SP.PORTAL_OPEN_KYR, "portal_drift_kmkyr": SP.PORTAL_DRIFT_KMKYR, "breeding": "mammal", "survival": "normal"},
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
        name: str | None = None, progress=lambda f, msg: None, climate_every: float = 2.0, split: bool = True,
        languages: bool = True) -> Path:
    tz, now0, world = R.resolve(ref)
    now1 = now0 if now is None else now

    def setup(w):
        ps = R.Pass(tz, now1, R.RecentParams(kyr=recent_kyr, climate_every=climate_every), world_ref=w)
        goods = None
        if w and tree.uses:
            progress(0.0, f"the land's goods (game attributes, resources, coasts) of world {w}")
            goods = LD.goods(w)
            if tree.mode == "real" and goods:  # (no fantasy goods in the real world)
                goods = {k: v for k, v in goods.items() if k not in SP.FANTASY_GOODS}
        return ps, goods

    # (PW-1265, the split history: a world refined finer than its time zoom (planet refine) has its history on the world it was
    # refined from up to the settled window, then on its own grid: history.handover. split=False runs it all on the refined grid)
    src = (S.read_header(S.find_world(world))["meta"].get("refined_from") or {}) if world else {}
    fine = None
    if split and src.get("world") and S.exists("world", src["world"]):
        fine = setup(world)
        ps, goods = setup(src["world"])
        if ps.grid.n == fine[0].grid.n:
            ps, goods, fine = fine[0], fine[1], None
    else:
        ps, goods = setup(world)
    h, res, pres = simulate(tree, ps, tries, progress, goods=goods, fine=fine)
    return save(h, res, pres, world=world, name=name, languages=languages)


def job(req: dict, progress=lambda f, msg: None) -> dict:
    """POST /api/lineages {world | timezoom, tree (name) | raw (the tree itself), tries}."""
    ref = req.get("world") or req.get("timezoom")
    if not ref:
        raise ValueError("give world or timezoom")
    tree = SP.parse(req["raw"], req.get("mode")) if req.get("raw") else load_tree(req["tree"], req.get("mode"))
    if req.get("tree"):
        tree.source = req["tree"]
    if req.get("gods_mode"):  # (PW-1309: asked for where the run is made; else the tree's meta.gods_mode)
        if req["gods_mode"] not in SP.GODS_MODES:
            raise ValueError(f"gods_mode must be one of {list(SP.GODS_MODES)}")
        tree.gods_mode = req["gods_mode"]
    out = run(str(ref).removesuffix(".json"), tree, int(req.get("tries", 4)), progress=progress,
              languages=req.get("languages", True) is not False)  # (planet make runs the pass as its own stage, PW-1634)
    return {"run": out.name}
