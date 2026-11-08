"""Which run, time zoom, world and zoom belong together (PW-472, PW-473): the
viewer's start screen lists these "planets", and its world navigator draws
one planet's provenance tree.

GET /api/planets -> {"planets": [...]}. A planet is one tectonic run and what
was made from it:

  run (Myr timeline)
    +- time zoom (kyr timeline, from a moment of the run)
    |    +- finished world (a frame of the time zoom)
    +- world (the run's keyframe sliced at a moment)
         +- zoom (a region of the world)
              +- fine zoom (a region of the zoom)

The links are the ones the store already records (store._run_item /
_world_item / _zoom_item: source_run, timezoom, world, parent_zoom), so
nothing new is stored. Worlds and time zooms whose run was deleted (or
that came from Earth, or from `planet generate`) form planets without a run.
"""

from __future__ import annotations

import json

from . import store as S

THUMB = "/api/thumb?kind={kind}&id={id}"


def _index(kind: str) -> list[dict]:
    p = {"run": S.runs_dir, "world": S.worlds_dir, "zoom": S.zooms_dir}[kind]() / "index.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return S.update_index(kind)


def build(runs: list[dict], worlds: list[dict], zooms: list[dict]) -> list[dict]:
    """Group index entries into planets (pure: tests drive it with plain dicts)."""
    run_by = {}
    for r in runs:
        run_by[r["dir"]] = r
        run_by[r["id"]] = r
    planets: dict[str, dict] = {}

    def planet(key: str, name: str, **kw) -> dict:
        return planets.setdefault(key, {"key": key, "name": name, "run": None, "nodes": [], **kw})

    def root_of(run_id) -> str | None:
        r = run_by.get(run_id)
        return r["dir"] if r else None

    for r in runs:
        if r.get("kind") in ("timezoom", "peoples"):
            continue
        p = planet(r["dir"], r["name"], seed=r["seed"], level=r["level"], myr=r["myr"], created=r["created"])
        p["run"] = r["dir"]
        p["nodes"].append({"key": f"run:{r['dir']}", "kind": "run", "id": r["dir"], "name": r["name"], "parent": None,
                           "created": r["created"], "myr": r["myr"], "level": r["level"], "seed": r["seed"],
                           "thumb": THUMB.format(kind="run", id=r["dir"])})
    where: dict[str, str] = {}  # node key -> planet key

    def home(src: str | None, fallback: str, name: str, item: dict) -> dict:
        """The planet something belongs to: its source run's, else one made for what is left of it."""
        if src and root_of(src):
            return planets[root_of(src)] if root_of(src) in planets else planet(root_of(src), name)
        key = f"gone:{src}" if src else f"loose:{fallback}"
        if src == "earth":
            key = "earth"
        return planet(key, item.get("source_run_name") or (f"run {src} (deleted)" if src and src != "earth" else name),
                      seed=item.get("seed"), level=item.get("level"), created=item.get("created"))

    for r in runs:
        if r.get("kind") not in ("timezoom", "peoples"):
            continue
        p = home(r.get("source_run"), r["dir"], r["name"], r)
        parent = f"run:{root_of(r['source_run'])}" if root_of(r.get("source_run")) else None
        if (r.get("phase") or r["kind"] == "peoples") and run_by.get(r.get("timezoom")):  # a recent pass / peoples run: under its time zoom
            parent = f"run:{run_by[r['timezoom']]['dir']}"
        p["nodes"].append({"key": f"run:{r['dir']}", "kind": r["kind"], "id": r["dir"], "name": r["name"], "parent": parent,
                           "created": r["created"], "at_myr": r["at_myr"], "kyr": r["kyr"], "level": r["level"],
                           **({"phase": r["phase"]} if r.get("phase") else {}), **({"world": r.get("world")} if r.get("phase") or r["kind"] == "peoples" else {}),
                           "thumb": THUMB.format(kind="run", id=r["dir"])})
        where[f"run:{r['dir']}"] = p["key"]
        if p["key"] == "earth":
            p["name"] = "Earth (ETOPO1)"
    world_ids = {w["id"] for w in worlds}
    for w in worlds:
        p = home(w.get("source_run"), w["id"], w["name"], w)
        parent = None
        if w.get("timezoom") and run_by.get(w["timezoom"]):
            parent = f"run:{run_by[w['timezoom']]['dir']}"
        elif w.get("source_run") and root_of(w["source_run"]):
            parent = f"run:{root_of(w['source_run'])}"
        if w.get("refined_from") in world_ids:  # a refined world (refine.py): under the world it was refined from
            parent = f"world:{w['refined_from']}"
        p["nodes"].append({"key": f"world:{w['id']}", "kind": "world", "id": w["id"], "file": w["file"], "name": w["name"],
                           "parent": parent, "created": w["created"], "t_myr": w.get("t_myr"),
                           "timezoom": w.get("timezoom"), "timezoom_kyr": w.get("timezoom_kyr"), "sea_level_change_m": w.get("sea_level_change_m"),
                           "level": w.get("level"), "refined_from": w.get("refined_from"),
                           "thumb": THUMB.format(kind="world", id=w["id"])})
        where[f"world:{w['id']}"] = p["key"]
    zoom_ids = {z["id"] for z in zooms}
    for z in zooms:
        pz = z.get("parent_zoom")
        parent = f"zoom:{pz}" if pz in zoom_ids else (f"world:{z['world']}" if z["world"] in world_ids else None)
        pk = where.get(parent) if parent else None
        if pk is None and pz:  # nested in a zoom: follow it up to its world
            up = next((q for q in zooms if q["id"] == pz), None)
            pk = where.get(f"world:{up['world']}") if up else None
        p = planets[pk] if pk else planet(f"gone:{z.get('source_run')}" if z.get("source_run") else f"loose:{z['id']}",
                                         z.get("world_name") or z["name"], created=z["created"])
        p["nodes"].append({"key": f"zoom:{z['id']}", "kind": "fine" if pz else "zoom", "id": z["id"], "name": z["name"],
                           "parent": parent, "created": z["created"], "world": z["world"], "center": z["center"],
                           "size_km": z["size_km"], "res_km": z["res_km"],
                           "thumb": f"/zooms/{z['id']}/preview.png"})
        where[f"zoom:{z['id']}"] = p["key"]
    out = []
    for p in planets.values():
        n = p["nodes"]
        p["counts"] = {k: sum(x["kind"] == k for x in n) for k in ("timezoom", "peoples", "world", "zoom", "fine")}
        p["created"] = p.get("created") or min((x["created"] for x in n), default="")
        p["updated"] = max((x["created"] for x in n), default=p["created"])
        # the picture on its card: its newest finished world, else a world, else the run
        pick = (sorted((x for x in n if x["kind"] == "world" and x.get("timezoom_kyr") is not None), key=lambda x: x["created"])
                or sorted((x for x in n if x["kind"] == "world"), key=lambda x: x["created"])
                or [x for x in n if x["kind"] in ("run", "timezoom")] or n)
        p["thumb"] = (pick[-1] if pick else {}).get("thumb")
        out.append(p)
    return sorted(out, key=lambda p: p["updated"], reverse=True)


def planets() -> list[dict]:
    return build(_index("run"), _index("world"), _index("zoom"))
