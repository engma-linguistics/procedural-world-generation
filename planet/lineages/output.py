"""The peoples' history stored as a run (kind 'peoples', PW-1394) and its report."""

from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM
from ..provenance import code_version
from . import cultures as CU
from . import demes as DM
from . import fuels as FU
from . import land as LD
from . import life_history as LH
from . import landuse as LU
from . import reputation as RP
from . import settlements as ST
from . import spec as SP
from . import techtree as TT
from .history import COMPOSITION_TWO_PCT, EST, PALETTE, History
from .history import megafauna as MG

U8 = lambda d: {"dtype": "uint8", "scale": 1, "offset": 0, "transform": None, "units": "", "description": d}  # noqa: E731
PEOPLE_LAYERS = {
    "peoples": U8("the people holding most of the cell (index into meta.lineages; 255 none)"),
    "peoples_mix": U8("how many peoples hold 25% or more of the cell"),
    "peoples_learned": U8("niche learning (PW-1155): % learned acceptance of the cell's leading people as a whole (peoples_whole; the most any of its lines learned here): 0 its culture's own country or none learned, 100 fully at home there up to its body limits"),
    "peoples_share": U8("% of the cell's habitat the leading people holds"),
    "peoples_overlay": U8("the strongest overlay people here (template or contact hybrid; index; 255 none)"),
    "peoples_whole": U8("the people holding most of the cell as a whole, its groups counted in (index; 255 none)"),
    "groups_best": U8("the group (a way of life within a people: steppe orcs, human farmers...) with most presence in the cell (index into meta.lineages; 255 none); a group's range at an era (PW-742)"),
    "groups_best_pct": U8("% of the cell's habitat the strongest group holds (groups_best)"),
    "mix_lead": U8("composition of the cell (PW-689): the people with most heads here (index; 255 none); peoples_whole stays the one holding most ground"),
    "mix_lead_share": U8("composition of the cell (PW-689): % of its people that are the leading one (mix_lead)"),
    "mix_second": U8("composition: the second people (index into meta.lineages; 255 none)"),
    "mix_second_share": U8("composition: % of the cell's people that are the second people"),
    "mix_other_share": U8("composition: % of the cell's people that are all the others together"),
}
ANIMAL_LAYERS = {  # (bit flags, one bit per animal in animal_defs.TABLE: 7 animals in two layers, not 14)
    "animal_wild": U8("bit flags: the animals whose wild range (suitability >= 0.35, animal_defs.wild_*) covers the cell; bit i = animal_defs.TABLE[i]; 0 in the deep epochs"),
    "animal_known": U8("bit flags: the animals tamed and known in the cell (0 before the taming; the front spreads over peopled land and, by boat, over the sea, animals.py); bit i = animal_defs.TABLE[i]"),
}
U64 = lambda d: {"dtype": "<u8", "scale": 1, "offset": 0, "transform": None, "units": "", "description": d}  # noqa: E731
U16 = lambda d: {"dtype": "<u2", "scale": 1, "offset": 0, "transform": None, "units": "", "description": d}  # noqa: E731
CROP_LAYERS = {  # (bit flags, one bit per crop in crop_defs.TABLE: 36 crops (at most 64) in two uint64 layers)
    "crop_wild": U64("bit flags: the crops whose wild range (suitability >= 0.35, crop_defs wild functions) covers the cell; bit i = crop_defs.TABLE[i]; 0 in the deep epochs"),
    "crop_known": U64("bit flags: the crops known in the cell and growable there (the grown range, crops.py GROWN_MIN; 0 before the first cultivation; the front of the knowledge spreads over peopled land and by canoe and boat); bit i = crop_defs.TABLE[i]"),
}
TERRAIN = {"elevation": S.LAYERS["elevation"], "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
           "temperature": S.LAYERS["temperature"], "climate": S.LAYERS["climate"], "tree_cover": S.LAYERS["tree_cover"],
           "precipitation": S.LAYERS["precipitation"]}


TINTS = ((1.0, 0.4), (0.0, 0.35), (1.0, 0.65), (0.0, 0.55), (1.0, 0.25), (0.0, 0.2))  # a group's: (toward white / black, by)


def tint(hexc: str, i: int) -> str:
    """The i-th group's colour: its people's, lightened or darkened in turn."""
    to, f = TINTS[i % len(TINTS)]
    c = [int(hexc.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)]
    return "#" + "".join(f"{round(v + (255 * to - v) * f):02x}" for v in c)


def colors(h: History) -> list[str]:
    out, used = [], 0
    for l in h.lines:
        if l.color:
            out.append(l.color)
        elif l.group_of:  # (a tint of its people's colour; the people comes first in the order)
            out.append(tint(out[h.idx[l.group_of]], h.tree.groups_of(l.group_of).index(l.id)))
        else:
            out.append(PALETTE[used % len(PALETTE)])
            used += 1
    return out


def save(h: History, res: dict, pres: dict, world: str | None = None, name: str | None = None) -> Path:
    g, ps = h.grid, h.ps
    frames = res["frames"]
    pres["homeland"] = homeland(h, res["present"], world)
    pres["stories"] = stories(h, pres)
    pres["composition"] = composition(h, res["frames"])
    pres["ascii"] = {"rows": ascii_present(h, res, 96, 36), "letters": {LETTERS[k % len(LETTERS)]: l.id for k, l in enumerate(h.lines)}}
    animal_layers = {**(ANIMAL_LAYERS if h.animals is not None else {}), **(CROP_LAYERS if h.crops is not None else {})}
    # body flags given as a share of a people (lactase persistence...): % of the cell's people with the trait (PW-701)
    animal_layers = {**animal_layers, **{f"body_{k}": U8(f"% of the cell's people with the body trait '{k}' (each people's share, mixed by the cell's composition)")
                                       for k in h.share_traits}}
    arrays = {k: [] for k in (*TERRAIN, *PEOPLE_LAYERS, *animal_layers)}
    out_frames = []
    for f in frames:
        env = f["env"]
        for k, spec in TERRAIN.items():
            v = env.get(k, np.zeros(g.n))
            arrays[k].append(S.encode(np.round(v) if k != "climate" else v, spec))
        for k in (*PEOPLE_LAYERS, *animal_layers):
            arrays[k].append(f[k])
        st = {kk: vv for kk, vv in f["stats"].items() if not isinstance(vv, (list, dict)) or kk in ("peoples", "learned")}  # (learned: PW-1155, Mkm² of learned country per line by biome)
        st["t"] = -round(f["ago"], 3)
        out_frames.append({"t": -round(f["ago"], 3), "stats": st, "omega": {}, "hotspots": [], "volcanoes": []})
    arrays = {k: np.stack(v) for k, v in arrays.items()}
    win = [(j, f) for j, f in enumerate(frames) if f.get("eraq")]  # frames recent enough to keep the land-use inputs of the fuels per era (PW-742)
    eraq_meta = None
    if win:
        eraq_meta = {"frames": [j for j, _ in win], "ago_kyr": [round(f["ago"], 3) for _, f in win], "keys": list(LU.ERA_KEYS),
                     "note": "uint8 per window frame (landuse.frame_inputs): dens log2p1, farm/herd/wood % of heads, herd_mult/farm_mult x20"}
    specs = {**TERRAIN, **PEOPLE_LAYERS, **animal_layers}
    run_id = S.new_id()
    out = S.path_of("run", run_id)
    layers = S.write_layers(out, arrays, specs)
    if eraq_meta:
        for k in LU.ERA_KEYS:
            (out / "layers" / f"eraq_{k}.bin").write_bytes(np.stack([f["eraq"][k] for _, f in win]).tobytes())
        eraq_meta["layers"] = {k: {"file": f"layers/eraq_{k}.bin", "dtype": "uint8", "shape": [len(win), g.n]} for k in LU.ERA_KEYS}
    if h.crops is not None:  # the present's crop facts for the cropland and the fuels (PW-721, PW-722), one frame each
        pres["crops"]["layers"] = {}
        for ck, cv in h.crops.present_cells().items():
            (out / "layers" / f"crops_{ck}.bin").write_bytes(np.round(np.clip(cv, 0, 1) * 100).astype(np.uint8).tobytes())
            pres["crops"]["layers"][ck] = {"file": f"layers/crops_{ck}.bin", "dtype": "uint8", "shape": [1, g.n], "units": "%",
                                           "description": {"know": "share of a staple diet the crops known and growable here make (crops.py)",
                                                           "straw": "mean stalks and straw the staple crops leave here, relative"}[ck]}
    for kind, owner in (("animals", h.animals), ("crops", h.crops)):  # how each cell came to know each stock (PW-742): 0 not known, 1 origin, 2 road (land front), 3 sea (boat)
        if owner is None or not pres.get(kind):
            continue
        for st in owner.stocks:
            if st.a.id in pres[kind]["stocks"]:
                (out / "layers" / f"route_{st.a.id}.bin").write_bytes(np.where(st.rd >= EST, st.route, 0).astype(np.uint8).tobytes())
                pres[kind]["stocks"][st.a.id]["route_file"] = f"layers/route_{st.a.id}.bin"
    presence_meta = write_presence(out, frames, len(h.lines), g.n)
    pres_q = np.round(np.clip(res["present"], 0, 1) * 100).astype(np.uint8)
    (out / "layers" / "presence_present.bin").write_bytes(pres_q.tobytes())
    S.write_grid(g)
    cols = colors(h)
    lines = [{"index": k, "id": l.id, "name": l.label(), "origin": l.origin, "parents": l.parents, "ago_kyr": l.ago_kyr, "sapient_kyr": l.sapient_kyr,
              "group_of": l.group_of, "groups": h.tree.groups_of(l.id),
              "extinct_kyr": l.extinct_kyr, "overlay": l.overlay, "realm": l.realm, "traits": l.traits, "color": cols[k],
              "leaf": l in h.tree.leaves(), "started_kyr": h.started.get(l.id), "ended_kyr": h.ended.get(l.id),
              "origin_place": h.origins.get(l.id), "track": h.tracks[l.id],
              "reached": {str(k): v for k, v in h.cross.reached.get(l.id, {}).items()},
              "crossings": h.crossings_n.get(l.id, 0), "story": pres["stories"].get(l.id),
              "demography": {**{kk: round(v, 4) for kk, v in l.demos().items()},  # (density: its mean over its land at the present, PW-1275)
                             "density": round(float((pres["lines"].get(l.id) or {}).get("density") or h.dens[k]), 4)}, "speed_kmyr": l.speed_kmyr,
              "body": l.body, "way": l.way, "generation_yr": h.gen_yr(l), "life_history": LH.summary(l),
              "life_eras": getattr(h, "life_eras", {}).get(l.id), "waves": getattr(h, "wave_log", {}).get(l.id),
              "faded_patches": h.faded.get(l.id, 0)} for k, l in enumerate(h.lines)]
    contacts = h.contacts.summary() if h.contacts is not None else None
    pres["reputation"] = RP.build(h.tree, contacts)  # what each people calls the others (PW-731)
    # the technology tree (PW-675 v0): which people knew what, and since when (techtree.py). With polities in the history switched
    # on (PW-1466) it is the calendar the history ran century by century (history.tech_live), finished here; else built now. D52's
    # town arms (B, E) need the settlement ledger, which needs the tree: the first tree goes without them (PW-1464, _towns_first)
    tt_args = (lines, contacts, pres, res["present"], h.goods, h.tree.mode, h.tree.era, h.seed)
    live_tt = getattr(h.rule, "tech", None)
    town_arms = TT.town_arms() if live_tt is None and world and eraq_meta else ""
    if live_tt is not None:
        techtree = live_tt.result(*tt_args[:5])
    else:
        techtree = TT.build(*tt_args, gods_mode=h.tree.gods_mode, landmass=h.cross.label, **({"arms": TT.arms_without_towns()} if town_arms else {}))
    m = ps.run["meta"]
    label = name or f"peoples: {h.tree.name} on {world or ps.run['id']}"
    events = [{"t": -e["ago_kyr"], "kind": e["kind"], "text": e["text"], "lat": e["lat"] if e["lat"] is not None else 0,
               "lon": e["lon"] if e["lon"] is not None else 0} for e in sorted(h.events, key=lambda e: -e["ago_kyr"])]
    S.write_json(out / "run.json", {
        "format": "procgen-run/2", "kind": "peoples", "id": run_id, "name": label,
        "meta": {"kind": "peoples", "time_unit": "kyr", **ps.meta(), "world": world,
                 "tree_name": h.tree.name, "mode": h.tree.mode, "portals": [{k: v for k, v in q.items() if k != "cell"} for q in (h._portals or [])], "thinnings": h.portal_report(),
                 "growth_rates": h.tree.growth_rates, "draw_ranges": h.tree.draw_ranges, "range_draws": h.ladder.drawn, "era": h.tree.era, "gods_mode": h.tree.gods_mode, "tree_file": h.tree.source, "tree": SP.to_raw(h.tree),
                 "disabled": h.tree.disabled, "lineages": lines, "animals": pres["animals"], "crops": pres.get("crops"),
                 "contacts": contacts, "techtree": techtree, "eraq": eraq_meta,
                 "land_use": None if h.goods is None else {"pull": h.tree.land_pull, "worked_out": h.goods["_made"],
                                                           "missing": h.goods["_missing"]}, "present": pres, "try_seed": h.seed,
                 "presence_present": {"file": "layers/presence_present.bin", "dtype": "uint8",
                                      "shape": [len(h.lines), g.n], "units": "%"},
                 "presence": presence_meta,
                 "kyr": round(max(fr["ago"] for fr in frames), 3), "step_kyr": ps.params.step, "every": ps.params.every,
                 "myr": max(fr["ago"] for fr in frames) / 1000, "frames": len(out_frames), "seed": m.get("seed"),
                 "level": g.level, "cells": g.n, "cell_size_km": round(g.spacing * R_KM), "params": m.get("params", {}),
                 "static_layers": [], "code": code_version(), "generated_in_s": round(h.runtime, 1),
                 "created": time.strftime("%Y-%m-%d %H:%M:%S")},
        "grid": f"../../grids/L{g.level}.json", "legend": S.legends(), "layers": layers,
        "events": events, "frames": out_frames})
    if hasattr(h.rule, "doc"):  # (polities in the history, when switched on, PW-1434: their record beside the read-out's)
        S.write_json(out / "polities_live.json", h.rule.doc())
    ledger_done = False
    if town_arms:
        techtree = _towns_first(out, tt_args, h.tree.gods_mode, techtree, h.cross.label)
        ledger_done = True
    report(out, h, res, pres)
    with open(out / "run.txt", "a") as f:
        f.write("\n".join(TT.lines_for_report(techtree, lines)) + "\n")
    if world:  # (peoples change the land, PW-662: needs the world's farmland)
        sm = LU.write(out)
        with open(out / "run.txt", "a") as f:
            f.write("\n".join(LU.lines_for_report(sm)) + "\n")
        FU.write(out)  # (what each people burns to cook: fuels.py, PW-722; adds a line to the stories and run.txt)
    DM.write(out)  # (the regional populations and their tree: demes.py, PW-981; demes.json, layers/demes.bin, meta.demes)
    CU.write(out)  # (emergent cultures from the demes: cultures.py, PW-670; cultures.json, meta.cultures)
    if (out / "cultures.json").exists():  # (gods and food taboos from the cultures: gods.py, taboos.py, PW-1306, PW-1305; readout only)
        from . import taboos as TB
        TB.write_religion(out, mode=h.tree.gods_mode)  # (the run's gods mode, PW-1309: chosen where the run is made)
    if world and eraq_meta:  # (the settlement ledger: settlements.py, PW-1011; settlements.json, meta.settlements)
        if ledger_done:  # (made by _towns_first from the final tree: only its run.txt section is still to write)
            ST.report_section(out)
        else:
            ST.write(out)
    T.update_index()
    return out


TOWN_PASSES = 3  # (_towns_first: at most this many ledger-and-tree rounds)


def _towns_first(out: Path, tt_args: tuple, gods_mode: str, tree0: dict, landmass=None) -> dict:
    """The tech tree with D52's town arms (B, E; PW-1464): the ledger from the tree made without them, then the tree again with the
    ledger's town footprint (techspread.town_footprint), until the techs the ledger reads (settlements.LEDGER_TECHS) stop moving,
    at most TOWN_PASSES rounds. Arm E touches only writing, the alphabet and law, which the ledger does not read, so it stops after
    one round; B also moves roads, copper and fortifications. Leaves meta.techtree and the ledger of the tree it returns."""
    from .techspread import town_footprint
    prev = tree0
    for i in range(TOWN_PASSES):
        ST.write(out, report=False)
        tt = TT.build(*tt_args, gods_mode=gods_mode, towns=town_footprint(out), landmass=landmass)
        S.update_meta(out, lambda r, tt=tt: r["meta"].__setitem__("techtree", tt))
        if ST.ledger_dates(tt["known"]) == ST.ledger_dates(prev["known"]):
            return tt  # (the ledger just written is the one this tree makes)
        prev = tt
    ST.write(out, report=False)  # (not settled after TOWN_PASSES: the ledger of the last tree, which a rebuild may still move)
    import warnings
    warnings.warn(f"tech tree town arms: the ledger still moved after {TOWN_PASSES} rounds", stacklevel=2)
    return prev


def write_presence(out: Path, frames: list, nlines: int, n: int) -> dict:
    """Every people's presence per frame (lane 109, PW-670), a sparse table: for frame f and line k the entries
    offsets[f, k]..offsets[f, k + 1] of `cells` (cell ids, ascending) and `share` (% of the cell's habitat, >= EST). The layers
    peoples_whole / mix_lead / mix_second keep only a cell's two leading peoples; this keeps them all, megafauna included."""
    cdt = np.uint16 if n <= 65536 else np.uint32
    offs = np.zeros((len(frames), nlines + 1), np.uint32)
    cells, share, at = [], [], 0
    for j, f in enumerate(frames):
        pl, pc, ps = f["presence"]
        offs[j] = at + np.searchsorted(pl, np.arange(nlines + 1))
        at += len(pl)
        cells.append(pc.astype(cdt))
        share.append(ps)
    files = {"offsets": "layers/presence_offsets.bin", "cells": "layers/presence_cells.bin", "share": "layers/presence_share.bin"}
    (out / files["offsets"]).write_bytes(offs.astype("<u4").tobytes())
    (out / files["cells"]).write_bytes(np.concatenate(cells).astype("<u2" if cdt is np.uint16 else "<u4").tobytes())
    (out / files["share"]).write_bytes(np.concatenate(share).astype(np.uint8).tobytes())
    return {"files": files, "entries": int(at), "lines": nlines, "frames": len(frames), "min_pct": round(100 * EST),
            "dtypes": {"offsets": "<u4", "cells": "<u2" if cdt is np.uint16 else "<u4", "share": "uint8"},
            "bytes": int(offs.nbytes + at * (np.dtype(cdt).itemsize + 1)),
            "description": "every whole people's presence per frame (megafauna and contact hybrids living on included): for frame f and "
                           "line k, entries offsets[f, k]..offsets[f, k+1] of cells (ascending) and share (% of the cell's habitat, at least min_pct)"}


def read_presence(run_dir: Path, meta: dict) -> dict | None:
    """The run's presence table (write_presence), or None on a run made before it: {"offsets" (frames, lines + 1), "cells", "share"}."""
    pm = meta.get("presence")
    if not pm:
        return None
    run_dir = Path(run_dir)
    out = {}
    for k, f in pm["files"].items():
        a = np.fromfile(run_dir / f, dtype=np.dtype(pm["dtypes"][k]))
        out[k] = a.reshape(pm["frames"], pm["lines"] + 1) if k == "offsets" else a
    return out


def read_presence_frame(run_dir: Path, meta: dict, frame: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One frame's slice of the presence table and of demes_all, read by seeking (the viewer's picker downloads one frame at a
    time, PW-1269): (cells, demes, offsets): the frame's entries for all lines in order, and offsets (lines + 1) of line k's entries within
    that slice. Raises KeyError (no table) or IndexError (no such frame)."""
    pm = meta.get("presence")
    if not pm:
        raise KeyError("this run has no presence table")
    if not 0 <= frame < pm["frames"]:
        raise IndexError(f"frame {frame} outside 0..{pm['frames'] - 1}")
    run_dir, w = Path(run_dir), pm["lines"] + 1
    with open(run_dir / pm["files"]["offsets"], "rb") as f:
        f.seek(4 * frame * w)
        row = np.frombuffer(f.read(4 * w), "<u4")
    a, b = int(row[0]), int(row[-1])
    cdt = np.dtype(pm["dtypes"]["cells"])
    with open(run_dir / pm["files"]["cells"], "rb") as f:
        f.seek(a * cdt.itemsize)
        cells = np.frombuffer(f.read((b - a) * cdt.itemsize), cdt)
    dm = (meta.get("demes") or {}).get("all")
    dem = np.zeros(0, "<u2")
    if dm:
        with open(run_dir / dm["file"], "rb") as f:
            f.seek(2 * a)
            dem = np.frombuffer(f.read(2 * (b - a)), "<u2")
    return cells, dem, row.astype(np.int64) - a


def composition(h: History, frames: list) -> dict:
    """How the peoples share the cells (PW-689): at the present and about 5 kyr ago, the share of peopled land with
    2+ peoples (a second people with at least history.COMPOSITION_TWO_PCT of the cell), the mean lead share, the empty
    land; the commonest pairs at the present; body flags given as a share (PW-701), mean over peopled land."""
    def at(ago):
        return min(frames, key=lambda f: abs(f["ago"] - ago))
    out = {"two_pct_min": COMPOSITION_TWO_PCT}
    for key, ago in (("present", 0.0), ("5kyr", 5.0)):
        f = at(ago)
        out[key] = {"ago_kyr": round(f["ago"], 2), **{k: f["stats"][k] for k in ("peopled_cells", "land_cells", "empty_land_pct", "two_plus_pct", "lead_share_mean_pct")}}
        sec, lead = f["mix_second_share"], f["peoples_whole"]
        out[key]["three_plus_pct"] = round(100 * float(((f["mix_other_share"] >= COMPOSITION_TWO_PCT) & (lead < 255)).sum() / max((lead < 255).sum(), 1)), 2)
        out[key]["second_3pct_pct"] = round(100 * float(((sec >= 3) & (lead < 255)).sum() / max((lead < 255).sum(), 1)), 2)
    f = frames[-1]
    pairs: dict[tuple, int] = {}
    sel = (f["mix_lead"] < 255) & (f["mix_second"] < 255) & (f["mix_second_share"] >= COMPOSITION_TWO_PCT)
    for a, b in zip(f["mix_lead"][sel].tolist(), f["mix_second"][sel].tolist()):
        pairs[(a, b)] = pairs.get((a, b), 0) + 1
    out["pairs"] = [{"lead": h.lines[a].id, "second": h.lines[b].id, "cells": n, "area_mkm2": round(n * h.cell_mkm2, 2)}
                    for (a, b), n in sorted(pairs.items(), key=lambda x: -x[1])[:10]]
    pop = f["peoples_whole"] < 255
    out["shares"] = {k: round(float(f["body_" + k][pop].mean()), 1) if pop.any() else 0.0 for k in h.share_traits}
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
                "template": f"appeared among the {', '.join(l.parents)}",
                "group": f"became a way of life among the {h.tree.lines[l.group_of].label() if l.group_of else '?'}, a culture of it rather than a split"}[l.origin]
        why = {"isolated part of the parent's range": "in an isolated part of its parent's land",
               "edge of the parent's range": "at the edge of its parent's land",
               "beside the parent's range (new niche)": "just beyond its parent's land, in a new niche",
               "where its way of life suits the land better than its people's":
                   "where its ways suited the land better than its people's",
               "at its people's range edge (no land suits it better there)": "at the edge of its people's land"}.get(o["why"], f"({o['why']})")
        s = [f"{l.label()[0].upper()}{l.label()[1:]} {what} ~{SP.years_ago(o['ago_kyr'])} {why}, on {where}."]
        for m, r in sorted(h.cross.reached.get(l.id, {}).items(), key=lambda x: -x[1]["ago_kyr"]):
            if r["how"] == "origin" or names[m]["area_mkm2"] < 0.05:
                continue
            how = {"land bridge": "walked over a land bridge (low sea) to", "strait": "crossed a strait to",
                   "overland": "spread overland (the land was joined then) to", "raft": "was carried on drift rafts to",
                   "coastal": "paddled to", "swims": "swam to", "flies": "flew to", "seafaring": "sailed to"}.get(r["how"], "reached")
            gap = f" over {r['gap_km']} km of open sea" if r.get("gap_km") else ""
            s.append(f"~{SP.years_ago(r['ago_kyr'])} it {how} {names[m]['name']}{gap}.")
        for e in h.events:
            if e["line"] == l.id and e["kind"] == "refuge":
                s.append(f"~{SP.years_ago(e['ago_kyr'])}, at its lowest, it held out in a refuge near {e['lat']:.0f}, {e['lon']:.0f}.")
            if e["line"] == l.id and e["kind"] == "lingers" and l.id in h._apart:  # (apart still at the present)
                s.append(f"~{SP.years_ago(e['ago_kyr'])} its parents' lands drew apart; it lived on as a people of its own "
                         f"near {e['lat']:.0f}, {e['lon']:.0f}.")
        p = pres["lines"].get(l.id)
        if l.id in h.ended and not p:
            s.append(f"It was gone by ~{SP.years_ago(h.ended[l.id])}" + (" (as its children took its land)." if h.tree.living_children(l.id) else "."))
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
        w = pres.get("peoples", {}).get(l.id)
        if w and len(w["living"]) > 1:  # (a people with groups: the whole)
            gl = [h.tree.lines[x].label() for x in w["living"] if x != l.id]
            s.append(f"With its cultures ({', '.join(gl)}) the {l.label()} are {people(w['population'])} in "
                     f"{w['area_mkm2']} Mkm²; {round(100 * w['shares'].get(l.id, 0))}% keep the old ways.")
        keeps = []
        crops = ((pres.get("crops") or {}).get("stocks") or {})
        for aid, hs in crops.items():
            tm = hs["tamed"]
            if not tm:
                continue
            if tm[0]["line"] == l.id:
                s.append(f"It was the first to cultivate {hs['noun']}, ~{SP.years_ago(tm[0]['ago_kyr'])} on {tm[0]['landmass_name']}.")
            elif any(t["line"] == l.id for t in tm[1:]):
                t = next(t for t in tm[1:] if t["line"] == l.id)
                s.append(f"It cultivated {hs['label']} again on its own ~{SP.years_ago(t['ago_kyr'])} on {t['landmass_name']}.")
        if crops and not l.overlay and LU.shares(h.tree, l)["farm"] >= 0.2:
            grown = sorted(((hs["adoption"].get(l.id, 0.0) * hs["weight"], hs["label"]) for hs in crops.values() if hs["adoption"].get(l.id, 0.0) >= 0.25), reverse=True)
            if grown:
                cn = [n for _, n in grown[:4]]
                s.append("Its fields grow mostly " + (", ".join(cn[:-1]) + " and " if len(cn) > 1 else "") + cn[-1] + ".")
        for aid, hs in ((pres.get("animals") or {}).get("stocks") or {}).items():
            tm, noun = hs["tamed"], hs["noun"]
            if not tm:
                continue
            if tm[0]["line"] == l.id:
                s.append(f"It was the first to tame the {noun}, ~{SP.years_ago(tm[0]['ago_kyr'])} on {'the ' + tm[0]['country'] + ' of ' if aid == 'horse' else ''}{tm[0]['landmass_name']}.")
            elif any(t["line"] == l.id for t in tm[1:]):
                t = next(t for t in tm[1:] if t["line"] == l.id)
                s.append(f"It tamed {hs['label']} again on its own ~{SP.years_ago(t['ago_kyr'])} on {t['landmass_name']}.")
            if hs["took_up_kyr"].get(l.id) is not None and hs["propensity"].get(l.id, 0) >= 0.3 and tm[0]["line"] != l.id:
                if aid == "horse":
                    s.append(f"It took up riding ~{SP.years_ago(hs['took_up_kyr'][l.id])} and rides today across {round(100 * hs['users_share'].get(l.id, 0))}% of its land.")
                else:
                    keeps.append(f"{hs['label']} (~{SP.years_ago(hs['took_up_kyr'][l.id])})")
        if keeps:
            s.append("It took up " + ", ".join(keeps[:-1]) + (" and " if len(keeps) > 1 else "") + keeps[-1] + ".")
        dy = ((pres.get("animals") or {}).get("dairy") or {}).get(l.id)
        if dy and dy["dairy_share"] >= 0.05:
            s.append(f"Its herders keep dairy herds of " + " and ".join(pres["animals"]["stocks"][x]["label"] for x in dy["animals"][:3]) + (", drinking the milk fresh" if dy["lactase_share"] >= 0.6 else ", souring and curdling the milk (few digest it fresh)") + ".")
        bn = SP.body_notes(l.body)
        if bn:
            s.append(f"The {l.label()} " + (", ".join(bn[:-1]) + (", and " if len(bn) > 2 else " and ") + bn[-1] if len(bn) > 1 else bn[0]) + ".")
        out[l.id] = " ".join(s)
    return out


def report(out: Path, h: History, res: dict, pres: dict) -> Path:
    L = [f"# Peoples {out.name}: {h.tree.name}", f"present = time zoom {h.ps.run['id']} @ {h.ps.now:g} kyr; tree "
         f"{h.tree.source or '(inline)'}; seed {h.seed}; tries {pres.get('tries')}; {h.runtime:.1f} s", ""]
    L.append(f"mode: {h.tree.mode}" + (f"; portals ({h.tree.portal_mode}): " + ", ".join(f"{q['kind']} {q['lat']},{q['lon']}" for q in h._portals or [])
                                      if h.tree.portal_mode != "off" else ""))
    L.append(f"target era: {h.tree.era} (a setting only: the technology tree, PW-675, will read it; the history is not run past the present)")
    if h.tree.disabled:
        L.append(f"switched off: {', '.join(h.tree.disabled)}")
    if h.goods is not None:
        L.append(f"land use: pull {h.tree.land_pull}; worked out here: {', '.join(h.goods['_made']) or 'none'}; "
                 f"missing on this world: {', '.join(h.goods['_missing']) or 'none'}")
    L += ["## Lines (letter on the map; '+' mixed, '.' unpeopled land, '#' ice)"]
    for k, l in enumerate(h.lines):
        o = h.origins.get(l.id)
        where = f"from {o['lat']:.0f},{o['lon']:.0f} at {SP.years_ago(o['ago_kyr'])} ({o['why']})" if o else "never appeared"
        p = pres["lines"].get(l.id)
        now = f"now {p['area_mkm2']} Mkm2 in {p['patches']} patch(es)" if p else \
            (f"ended {SP.years_ago(h.ended.get(l.id))}" if l.id in h.ended else "absent")
        L.append(f"  {LETTERS[k % len(LETTERS)]} {l.label():<22} {l.origin:<8} {where}; {now}")
    an = pres.get("animals")
    if an:
        L += ["", "## Animals (PW-691) and boats (PW-688)", "  craft that carry animals over the sea: " + "; ".join(
            f"{c['name']} since {SP.years_ago(c['since_kyr'])}, {c['reach_km']:g} km, carries {c['carries_up_to']}" for c in an["craft"])]
        for aid, hs in an["stocks"].items():
            tag = f" [{an['mode']} mode: {'fantasy animal' if hs['fantasy'] else 'real'}]" if hs["fantasy"] else ""
            L += [f"  {hs['label']}{tag}: {hs['wild_mkm2']} Mkm² of wild range at the present; known over {hs['known_mkm2']} Mkm² "
                  f"({hs['known_on_wild_mkm2']} Mkm² of it wild range); crossed the sea {hs['crossed']} time(s)"]
            L += [f"    tamed ~{SP.years_ago(t['ago_kyr'])} by the {t['people']} on the {t['country']} of {t['landmass_name']} "
                  f"({t['lat']}, {t['lon']}; {t['wild_mkm2']} Mkm² of wild range there)" + ("" if t["first"] else " (again, on its own)")
                  for t in hs["tamed"]] or [f"    never tamed: {hs['never']} (date drawn {SP.years_ago(hs['date_drawn_kyr'])})"]
            L += [f"    by boat: {c['landmass_name']}, {SP.years_ago(c['ago_kyr'])}, {c['craft']}, {c['gap_km']} km" for c in hs["crossings"][:6]]
            L += ["    users (share of their land): " + ", ".join(f"{k} {round(100 * v)}%" for k, v in sorted(hs["users_share"].items(), key=lambda x: -x[1])[:8] if v > 0.01)]
        if an["dairy"]:
            L += ["  dairy (herd share x land with a dairy animal): " + ", ".join(
                f"{k} {round(100 * v['dairy_share'])}% ({', '.join(v['animals'])})" for k, v in an["dairy"].items())]
    cr = pres.get("crops")
    if cr:
        L += ["", "## Crops (PW-721)", f"  mean share of a staple diet the crops known and growable make on peopled land: {cr['know_mean_peopled']}"]
        for aid, hs in cr["stocks"].items():
            tag = f" [{cr['mode']} mode: fantasy crop]" if hs["fantasy"] else ""
            L += [f"  {hs['label']}{tag}: {hs['wild_mkm2']} Mkm² of wild range at the present; grown over {hs['grown_mkm2']} Mkm² "
                  f"(known over {hs['known_mkm2']}); crossed the sea {hs['crossed']} time(s)"]
            L += [f"    {'first ' if t['first'] else ''}cultivated ~{SP.years_ago(t['ago_kyr'])} by the {t['people']} on {t['landmass_name']} "
                  f"({t['lat']}, {t['lon']}; {t['wild_mkm2']} Mkm² of wild range there)" + ("" if t["first"] else " (again, on its own)")
                  for t in hs["tamed"]] or [f"    never cultivated: {hs['never']} (date drawn {SP.years_ago(hs['date_drawn_kyr'])})"]
    mf = pres.get("megafauna")
    if mf:
        L += ["", "## Megafauna (PW-924: counted, exempt from the peoples' range targets)"]
        L += [f"  {MG.line_text(lid, h.tree.lines[lid].label(), r)}" for lid, r in mf.items()]
        L += [f"  {t}" for t in MG.ages_text(pres.get("megafauna_ages") or {})]
    L += ["", "## Stories"] + [f"  {t}" for t in pres.get("stories", {}).values()]
    L += ["", "## Events"] + [f"  {SP.years_ago(e['ago_kyr']):>22}  {e['text']}" for e in sorted(h.events, key=lambda e: -e["ago_kyr"])]
    mx = pres.get("mixing", {})
    L += ["", f"## Mixing at the present: {mx.get('area_mkm2')} Mkm2 ({mx.get('land_share')} of the land; corridor land "
              f"{mx.get('in_corridors')} mixed, closed land {mx.get('in_closed')}); empty continents: "
              f"{', '.join(pres.get('empty_continents') or []) or 'none'}; lost: {', '.join(pres.get('lost') or []) or 'none'}"]
    cp = pres.get("composition")
    if cp:
        L += ["", f"## Who lives together (PW-689): peopled land with a second people of at least {cp['two_pct_min']}% of the cell"]
        for key, lab in (("5kyr", "about 5 kyr ago"), ("present", "present")):
            c = cp[key]
            L.append(f"  {lab:<16} {c['two_plus_pct']}% with 2+ peoples ({c['second_3pct_pct']}% with a second of 3% or more; "
                     f"{c['three_plus_pct']}% with 10%+ of others besides); the leader holds {c['lead_share_mean_pct']}% of a cell on average; "
                     f"{c['empty_land_pct']}% of the land is empty ({c['peopled_cells']} of {c['land_cells']} land cells peopled)")
        L += ["  commonest pairs: " + ", ".join(f"{p['lead']}+{p['second']} {p['area_mkm2']} Mkm²" for p in cp["pairs"][:6])]
        for k, v in cp["shares"].items():
            L.append(f"  body '{k}': {v}% of the people on peopled land (each people's share, mixed by the cells' composition)")
    L += ["## Numbers at the present (presence x density x area)"] + [
        f"  {lid:<18} {v.get('population', 0):>12,} people  {v.get('density', 0):g}/km² (a band of {SP.BAND} roams "
        f"{v.get('band_km2', 0):g} km²)  {v['area_mkm2']} Mkm²" + (f"; {v['faded_patches']} patch-fadings below the viable number (patches x checks)" if v.get('faded_patches') else "")
        for lid, v in sorted(pres["lines"].items(), key=lambda x: -x[1].get("population", 0))]
    if pres.get("peoples"):
        L += ["", "## Peoples with their groups (cultures, PW-665)"]
        for lid, w in pres["peoples"].items():
            L.append(f"  {lid:<18} {w['population']:>12,} people  {w['area_mkm2']} Mkm² in {w['patches']} patch(es): "
                     + ", ".join(f"{x} {round(100 * v)}%" for x, v in w["shares"].items()))
    L += ["", "## Landmasses: who found them first"] + [
        f"  {nm['name']}: held {nm['held_share']}; " + (f"first {nm['discovered']['by']} {SP.years_ago(nm['discovered']['ago_kyr'])} ({nm['discovered']['how']}"
                                                         + (f", {nm['discovered']['gap_km']} km" if nm['discovered'].get('gap_km') else "") + ")"
                                                         if nm.get("discovered") else "never reached")
        + (f"; of today's peoples {nm['settled_by']['by']} {SP.years_ago(nm['settled_by']['ago_kyr'])} ({nm['settled_by']['how']}"
           + (f", {nm['settled_by']['gap_km']} km" if nm['settled_by'].get('gap_km') else "") + ")" if nm.get("settled_by") else "")
        for nm in pres.get("landmasses", [])[:16]]
    if pres.get("try_stats"):
        top = max(x["wish_score"] for x in pres["try_stats"])
        L += ["", "## Tries (PW-707: judge changes on the mean; the best-of-N pick moves by chance)"]
        L += [f"  try {k}{' *' if t['wish_score'] == top else ''}: wish {t['wish_score'] if pres['wishes'] else 'n/a (no wishes)'}, empty land {t['empty_land_pct']}%, "
              f"two+ peoples {t['two_plus_pct']}%, lead share {t['lead_share_mean_pct']}%, lost {t['lost']}"
              for k, t in enumerate(pres["try_stats"])]
        L += ["  mean: " + ", ".join(f"{q} {v}" for q, v in pres["tries_mean"].items())]
    L += ["", "## Mixing zones at the present"] + [f"  {z['area_mkm2']:>6} Mkm2 near {z['lat']},{z['lon']}: {', '.join(z['lines'])}"
                                                   for z in pres["mixing_zones"][:12]] or ["  (none)"]
    L += ["", "## Neighbours at the present"] + [f"  {lid}: {', '.join(v['neighbours'])}" for lid, v in pres["lines"].items()]
    if pres["wishes"]:
        L += ["", f"## Wishes (score {pres['wish_score']} over {pres.get('wishes_counted')} counted of {len(pres['wishes'])}; "
                  f"every wish, uncontested ones too: {pres.get('wish_score_raw')}; tries {pres.get('tries')})"]
        L += [f"  {w['a']} {w['want']} {w.get('b') or ''}: {w['score']}"
              + (f" (niches alone would put {w['baseline']:.0%} of a's habitat near b's" + ("" if w.get("contested", True) else "; not counted") + ")"
                 if "baseline" in w else "") for w in pres["wishes"]]
    L += ["", "## Present day"] + ascii_present(h, res)
    path = out / "run.txt"
    S.write_atomic(path, "\n".join(L) + "\n")
    return path
