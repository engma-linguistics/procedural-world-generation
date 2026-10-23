"""The peoples' history stored as a run (kind timezoom, meta.phase 'lineages') and its report."""

from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM
from ..provenance import code_version
from . import land as LD
from . import spec as SP
from .history import EST, PALETTE, History

U8 = lambda d: {"dtype": "uint8", "scale": 1, "offset": 0, "transform": None, "units": "", "description": d}  # noqa: E731
PEOPLE_LAYERS = {
    "peoples": U8("the people holding most of the cell (index into meta.lineages; 255 none)"),
    "peoples_mix": U8("how many peoples hold 25% or more of the cell"),
    "peoples_share": U8("% of the cell's habitat the leading people holds"),
    "peoples_overlay": U8("the strongest overlay people here (template or contact hybrid; index; 255 none)"),
}
TERRAIN = {"elevation": S.LAYERS["elevation"], "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
           "temperature": S.LAYERS["temperature"], "climate": S.LAYERS["climate"], "tree_cover": S.LAYERS["tree_cover"],
           "precipitation": S.LAYERS["precipitation"]}


def colors(h: History) -> list[str]:
    out, used = [], 0
    for l in h.lines:
        if l.color:
            out.append(l.color)
        else:
            out.append(PALETTE[used % len(PALETTE)])
            used += 1
    return out


def save(h: History, res: dict, pres: dict, world: str | None = None, name: str | None = None) -> Path:
    g, ps = h.grid, h.ps
    frames = res["frames"]
    pres["homeland"] = homeland(h, res["present"], world)
    pres["stories"] = stories(h, pres)
    pres["ascii"] = {"rows": ascii_present(h, res, 96, 36), "letters": {LETTERS[k % len(LETTERS)]: l.id for k, l in enumerate(h.lines)}}
    arrays = {k: [] for k in (*TERRAIN, *PEOPLE_LAYERS)}
    out_frames = []
    for f in frames:
        env = f["env"]
        for k, spec in TERRAIN.items():
            v = env.get(k, np.zeros(g.n))
            arrays[k].append(S.encode(np.round(v) if k != "climate" else v, spec))
        for k in PEOPLE_LAYERS:
            arrays[k].append(f[k])
        st = {kk: vv for kk, vv in f["stats"].items() if not isinstance(vv, (list, dict)) or kk == "peoples"}
        st["t"] = -round(f["ago"], 3)
        out_frames.append({"t": -round(f["ago"], 3), "stats": st, "omega": {}, "hotspots": [], "volcanoes": []})
    arrays = {k: np.stack(v) for k, v in arrays.items()}
    specs = {**TERRAIN, **PEOPLE_LAYERS}
    run_id = S.new_id()
    out = S.path_of("run", run_id)
    layers = S.write_layers(out, arrays, specs)
    pres_q = np.round(np.clip(res["present"], 0, 1) * 100).astype(np.uint8)
    (out / "layers" / "presence_present.bin").write_bytes(pres_q.tobytes())
    S.write_grid(g)
    cols = colors(h)
    lines = [{"index": k, "id": l.id, "name": l.label(), "origin": l.origin, "parents": l.parents, "ago_kyr": l.ago_kyr,
              "extinct_kyr": l.extinct_kyr, "overlay": l.overlay, "traits": l.traits, "color": cols[k],
              "leaf": l in h.tree.leaves(), "started_kyr": h.started.get(l.id), "ended_kyr": h.ended.get(l.id),
              "origin_place": h.origins.get(l.id), "track": h.tracks[l.id],
              "reached": {str(k): v for k, v in h.cross.reached.get(l.id, {}).items()},
              "crossings": h.crossings_n.get(l.id, 0), "story": pres["stories"].get(l.id),
              "demography": {kk: round(v, 4) for kk, v in l.demos().items()}, "speed_kmyr": l.speed_kmyr,
              "faded_patches": h.faded.get(l.id, 0)} for k, l in enumerate(h.lines)]
    m = ps.run["meta"]
    label = name or f"peoples: {h.tree.name} on {world or ps.run['id']}"
    events = [{"t": -e["ago_kyr"], "kind": e["kind"], "text": e["text"], "lat": e["lat"] if e["lat"] is not None else 0,
               "lon": e["lon"] if e["lon"] is not None else 0} for e in sorted(h.events, key=lambda e: -e["ago_kyr"])]
    S.write_json(out / "run.json", {
        "format": "procgen-run/2", "kind": "timezoom", "id": run_id, "name": label,
        "meta": {"kind": "timezoom", "phase": "lineages", "time_unit": "kyr", **ps.meta(), "world": world,
                 "tree_name": h.tree.name, "tree_file": h.tree.source, "tree": SP.to_raw(h.tree),
                 "disabled": h.tree.disabled, "lineages": lines,
                 "land_use": None if h.goods is None else {"pull": h.tree.land_pull, "worked_out": h.goods["_made"],
                                                           "missing": h.goods["_missing"]}, "present": pres, "try_seed": h.seed,
                 "presence_present": {"file": "layers/presence_present.bin", "dtype": "uint8",
                                      "shape": [len(h.lines), g.n], "units": "%"},
                 "kyr": round(max(fr["ago"] for fr in frames), 3), "step_kyr": ps.params.step, "every": ps.params.every,
                 "myr": max(fr["ago"] for fr in frames) / 1000, "frames": len(out_frames), "seed": m.get("seed"),
                 "level": g.level, "cells": g.n, "cell_size_km": round(g.spacing * R_KM), "params": m.get("params", {}),
                 "static_layers": [], "code": code_version(), "generated_in_s": round(h.runtime, 1),
                 "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{g.level}.json", "legend": S.legends(), "layers": layers,
        "events": events, "frames": out_frames})
    report(out, h, res, pres)
    T.update_index()
    return out


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def ascii_present(h: History, res: dict, w: int = 120, hh: int = 40) -> list[str]:
    g = h.grid
    f = res["frames"][-1]
    lat = np.linspace(80, -80, hh)
    lon = np.linspace(-180, 180, w, endpoint=False)
    LA, LO = np.radians(np.meshgrid(lat, lon, indexing="ij"))
    pts = np.stack([np.cos(LA) * np.cos(LO), np.cos(LA) * np.sin(LO), np.sin(LA)], -1).reshape(-1, 3)
    cell = g.locate(pts).reshape(hh, w)
    land, ice, dom, mix = f["env"]["land"], f["env"]["ice"] > 0.5, f["peoples"], f["peoples_mix"]
    rows = []
    for r in range(hh):
        s = []
        for c in cell[r]:
            if not land[c]:
                s.append(" ")
            elif ice[c]:
                s.append("#")
            elif dom[c] == 255:
                s.append(".")
            else:
                s.append(LETTERS[dom[c] % len(LETTERS)] if mix[c] < 2 else "+")
        rows.append("".join(s))
    return rows


def people(n: float) -> str:
    """A rough head count in words: 'about 7,000', '1.2 million'."""
    n = float(n)
    if n >= 1e6:
        return f"{n / 1e6:.2g} million"
    if n >= 100:
        return f"about {int(float(f'{n:.2g}')):,}"
    return f"a few dozen" if n >= 20 else "a handful"


def _ago(kyr: float) -> str:
    if kyr >= 1000:
        return f"{kyr / 1000:.3g} Myr"
    if kyr >= 1:
        return f"{kyr:.3g} kyr"
    return f"{max(round(kyr * 10) * 100, 100):.0f} years"


def homeland(h: History, P: np.ndarray, world: str | None) -> dict[str, list[str]]:
    """Per living people, what its land gives it (land.homeland_notes) for the goods its way of life looks for."""
    if h.goods is None:
        return {}
    uses, held = {}, {}
    for k, l in enumerate(h.lines):
        if l.origin == "template":
            continue
        u = h.tree.uses_of(l)
        if not u:
            continue
        uses[l.id] = u
        held[l.id] = h._linger[k] if l.overlay else P[k] >= 0.25
    return LD.homeland_notes(h.grid, uses, held, h.goods, LD.landmarks(world), h.cell_mkm2)


def stories(h: History, pres: dict) -> dict[str, str]:
    """Per people, a few game-ready sentences from its history: where and why it arose, its crossings,
    refuges and end, and where it lives at the present (and with whom)."""
    out = {}
    names = h.cross.names
    for k, l in enumerate(h.lines):
        o = h.origins.get(l.id)
        if not o:
            out[l.id] = f"{l.label()} never appeared on this world."
            continue
        lm = int(h.cross.label[o["cell"]]) if h.cross.label[o["cell"]] >= 0 else -1
        where = names[lm]["name"] if lm >= 0 else f"land now under the sea near {o['lat']:.0f}, {o['lon']:.0f}"
        what = {"root": "arose", "split": f"split from the {h.tree.lines[l.parents[0]].label() if l.parents and l.parents[0] in h.tree.lines else '?'}",
                "arrival": "arrived from beyond the world", "hybrid": f"first appeared where {' and '.join(l.parents)} met",
                "template": f"appeared among the {', '.join(l.parents)}"}[l.origin]
        why = {"isolated part of the parent's range": "in an isolated part of its parent's land",
               "edge of the parent's range": "at the edge of its parent's land",
               "beside the parent's range (new niche)": "just beyond its parent's land, in a new niche"}.get(o["why"], f"({o['why']})")
        s = [f"{l.label()[0].upper()}{l.label()[1:]} {what} ~{_ago(o['ago_kyr'])} ago {why}, on {where}."]
        for m, r in sorted(h.cross.reached.get(l.id, {}).items(), key=lambda x: -x[1]["ago_kyr"]):
            if r["how"] == "origin" or names[m]["area_mkm2"] < 0.05:
                continue
            how = {"land bridge": "walked over a land bridge (low sea) to", "strait": "crossed a strait to",
                   "overland": "spread overland (the land was joined then) to", "raft": "was carried on drift rafts to",
                   "coastal": "paddled to", "swims": "swam to", "flies": "flew to", "seafaring": "sailed to"}.get(r["how"], "reached")
            gap = f" over {r['gap_km']} km of open sea" if r.get("gap_km") else ""
            s.append(f"~{_ago(r['ago_kyr'])} ago it {how} {names[m]['name']}{gap}.")
        for e in h.events:
            if e["line"] == l.id and e["kind"] == "refuge":
                s.append(f"~{_ago(e['ago_kyr'])} ago, at its lowest, it held out in a refuge near {e['lat']:.0f}, {e['lon']:.0f}.")
            if e["line"] == l.id and e["kind"] == "lingers" and l.id in h._apart:  # (apart still at the present)
                s.append(f"~{_ago(e['ago_kyr'])} ago its parents' lands drew apart; it lived on as a people of its own "
                         f"near {e['lat']:.0f}, {e['lon']:.0f}.")
        p = pres["lines"].get(l.id)
        if l.id in h.ended and not p:
            s.append(f"It was gone by ~{_ago(h.ended[l.id])} ago" + (" (as its children took its land)." if h.tree.living_children(l.id) else "."))
        elif p:
            nb = [h.tree.lines[x].label() for x in list(p["neighbours"])[:4] if x in h.tree.lines]
            iso = "one land" if p["patches"] == 1 else f"{p['patches']} separate lands (the largest {round(100 * p['largest_patch_share'])}%)"
            s.append(f"Today: {people(p.get('population', 0))} in {p['area_mkm2']} Mkm² in {iso}"
                     + (f"; neighbours {', '.join(nb)}." if nb else "; no neighbours."))
            if p.get("own_mkm2"):
                s.append(f"Of that, {p['own_mkm2']} Mkm² is a land of its own, where its parents no longer meet.")
            hl = pres.get("homeland", {}).get(l.id)
            if hl:
                s.append(f"The {l.label()} " + "; and they ".join(hl) + ".")
        out[l.id] = " ".join(s)
    return out


def report(out: Path, h: History, res: dict, pres: dict) -> Path:
    L = [f"# Peoples {out.name}: {h.tree.name}", f"present = time zoom {h.ps.run['id']} @ {h.ps.now:g} kyr; tree "
         f"{h.tree.source or '(inline)'}; seed {h.seed}; tries {pres.get('tries')}; {h.runtime:.1f} s", ""]
    if h.tree.disabled:
        L.append(f"switched off: {', '.join(h.tree.disabled)}")
    if h.goods is not None:
        L.append(f"land use: pull {h.tree.land_pull}; worked out here: {', '.join(h.goods['_made']) or 'none'}; "
                 f"missing on this world: {', '.join(h.goods['_missing']) or 'none'}")
    L += ["## Lines (letter on the map; '+' mixed, '.' unpeopled land, '#' ice)"]
    for k, l in enumerate(h.lines):
        o = h.origins.get(l.id)
        where = f"from {o['lat']:.0f},{o['lon']:.0f} at {o['ago_kyr']:g} kyr ago ({o['why']})" if o else "never appeared"
        p = pres["lines"].get(l.id)
        now = f"now {p['area_mkm2']} Mkm2 in {p['patches']} patch(es)" if p else \
            (f"ended {h.ended.get(l.id):g} kyr ago" if l.id in h.ended else "absent")
        L.append(f"  {LETTERS[k % len(LETTERS)]} {l.label():<22} {l.origin:<8} {where}; {now}")
    L += ["", "## Stories"] + [f"  {t}" for t in pres.get("stories", {}).values()]
    L += ["", "## Events"] + [f"  {e['ago_kyr']:>9.2f} kyr ago  {e['text']}" for e in sorted(h.events, key=lambda e: -e["ago_kyr"])]
    mx = pres.get("mixing", {})
    L += ["", f"## Mixing at the present: {mx.get('area_mkm2')} Mkm2 ({mx.get('land_share')} of the land; corridor land "
              f"{mx.get('in_corridors')} mixed, closed land {mx.get('in_closed')}); empty continents: "
              f"{', '.join(pres.get('empty_continents') or []) or 'none'}; lost: {', '.join(pres.get('lost') or []) or 'none'}"]
    L += ["## Numbers at the present (presence x density x area)"] + [
        f"  {lid:<18} {v.get('population', 0):>12,} people  {v.get('density', 0):g}/km² (a band of {SP.BAND} roams "
        f"{v.get('band_km2', 0):g} km²)  {v['area_mkm2']} Mkm²" + (f"; {v['faded_patches']} patch-fadings below the viable number (patches x checks)" if v.get('faded_patches') else "")
        for lid, v in sorted(pres["lines"].items(), key=lambda x: -x[1].get("population", 0))]
    L += ["", "## Landmasses: who found them first"] + [
        f"  {nm['name']}: held {nm['held_share']}; " + (f"first {nm['discovered']['by']} {_ago(nm['discovered']['ago_kyr'])} ago ({nm['discovered']['how']}"
                                                         + (f", {nm['discovered']['gap_km']} km" if nm['discovered'].get('gap_km') else "") + ")"
                                                         if nm.get("discovered") else "never reached")
        + (f"; of today's peoples {nm['settled_by']['by']} {_ago(nm['settled_by']['ago_kyr'])} ago ({nm['settled_by']['how']}"
           + (f", {nm['settled_by']['gap_km']} km" if nm['settled_by'].get('gap_km') else "") + ")" if nm.get("settled_by") else "")
        for nm in pres.get("landmasses", [])[:16]]
    L += ["", "## Mixing zones at the present"] + [f"  {z['area_mkm2']:>6} Mkm2 near {z['lat']},{z['lon']}: {', '.join(z['lines'])}"
                                                   for z in pres["mixing_zones"][:12]] or ["  (none)"]
    L += ["", "## Neighbours at the present"] + [f"  {lid}: {', '.join(v['neighbours'])}" for lid, v in pres["lines"].items()]
    if pres["wishes"]:
        L += ["", f"## Wishes (score {pres['wish_score']}; tries {pres.get('tries')})"]
        L += [f"  {w['a']} {w['want']} {w.get('b') or ''}: {w['score']}" for w in pres["wishes"]]
    L += ["", "## Present day"] + ascii_present(h, res)
    path = out / "run.txt"
    S.write_atomic(path, "\n".join(L) + "\n")
    return path
