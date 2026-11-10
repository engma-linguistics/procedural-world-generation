"""`planet serve`: the viewer's HTTP server.

  GET    /viewer/...                  the viewer (from the repository)
  GET    /runs/..., /worlds/..., /zooms/..., /grids/...
                                      outputs, from the data root (store.root())
  DELETE /runs/<id>, /worlds/<id>, /zooms/<id>
                                      delete one item (store.delete; a world
                                      takes its zooms and highlights with it)
  POST   /api/zoom, /api/timezoom, /api/finish, /api/make, /api/highlight-zooms, /api/refine
                                      start a job (api.py; make.py: seed to finished world) -> {"job": id}
  GET    /api/refine/estimate?world=<id>&level=8   a refine's cost and whether there is room for it (api.refine_estimate)
  GET    /api/presence?run=&frame=    one frame of a peoples run's presence table + demes_all (binary; the demes picker, PW-1269)
  DELETE /api/jobs/<id>               cancel a queued or running job (api.Jobs.cancel)
  GET    /api/planets                 runs, time zooms, worlds and zooms grouped by provenance (family.py)
  GET    /api/thumb?kind=run|world&id=<id>   a small PNG preview (thumbs.py; &proj=equal-earth|equirect &w=192|512|1024)
  GET    /api/make/options, /api/make/estimate?seed=&preset=&level=...   the New planet form (make.py)
  GET    /api/sections?world=<id>     the 54 tiling sections of a world: centre, up, corners, land share, built zooms
  GET    /api/jobs/<id>               a job's progress / result
  GET    /api/jobs?type=refine        {"active": the queued or running job of that type, or null} (a page opened later follows it)
  GET    /api/highlights?run=<id>&t=<Myr> or ?world=<id>   (api.highlights)
  GET    /api/brief?run=<id>&people=<id>|culture=<id>[&era=<kyr>] or &region=lat,lon[,km]   the culinary brief (brief()); a culture's has its cuisine sheet
  GET    /api/speak?ipa=<url-encoded IPA>[&people=<lineage id>][&backend=auto|espeak|piper][&sentence=1[&q=1]][&stress=initial|penult|final]   a word
         (or, with sentence=1, a whole sentence with word gaps and phrase intonation; q=1 a yes/no question) said aloud: audio/wav
  GET    /api/speak/backends          {"backends": [...available], "default": "piper"|"espeak"|null}
  GET    /api/cultures?run=<id>      a peoples run's emergent cultures (cultures()): its cultures.json, else worked out on the fly, not saved
  GET    /api/gods?run=<id>[&mode=]  the gods of those cultures (lineages/gods.py, PW-1306) and their faiths (PW-1358): its gods.json, else worked out on the fly, not saved
  GET    /api/authored?run=<id>[&choices=1]   the faiths written in for a run, its saved gods mode and the invasions scheduled (its authored.json, PW-1430, PW-1433); choices: the peoples and cultures (by uid) a row may name
  POST   /api/authored {run, faiths, gods_mode, invasions}   check and save them (any left out are kept; the run's authored.json, the only file this writes into a run)
  GET    /api/taboos?run=<id>        the taboos of those cultures (lineages/taboos.py, PW-1305, PW-1311): its taboos.json, else worked out, not saved
  GET    /api/faithmap?run=<id>&frame=<f>[&w=1024][&only=<faith>]   where each faith was at one stored frame, an equirectangular PNG (lineages/faithmap.py)
  GET    /api/polities?run=<id>[&ago=<kyr>]   who rules where (lineages/polities.py, PW-1431): the polities and per-step counts; with ago, the nearest century step's map
  GET    /api/techspread?run=<id>[&tech=writing]   how fast one tech spread (lineages/techspread.py): who knew it when and how, the share of settled people over time
  GET    /api/trade?run=<id>[&culture=<id>]   the goods ledger (lineages/trade.py, PW-1502): per way of life, or one culture's surplus and lacks per era; &flows=1: where its goods come from and go (trade_flow.py, PW-1503); &routes=1&ago=<kyr>: that era's trade routes and trading towns (trade_routes.py, PW-1504)
  GET    /api/tongues?run=<id>[&culture=<id>|&ago=<kyr>]   the tongues ledger (lineages/tongues.py, PW-1526): per culture and era the tongues its people speak besides its own; trade languages and pidgins per era
  POST   /api/names {world, letter, name}   rename a landmass (names.set_name; empty name clears)
  GET    /api/favourites[?kind=run|world|zoom]   the starred items [{kind, id, starred}] (favourites.py)
  POST   /api/favourites {kind, id, starred}   star or unstar one; answers the new list
  GET    /api/cell?world=<id>&i=<cell>  one world cell's 12 months (cell())

Big data files (.bin run layers, .json worlds and grids) go gzipped when the
browser accepts it (Content-Encoding: gzip), compressed once and cached under
<data root>/.gzcache (Handler.send_gzip). Derived gods and taboos docs are kept
under <data root>/.godscache (disk_cached), so a restart doesn't pay again; so is the polities
doc (polities_doc) and the goods ledger (trade_doc), read after the run and never written into it.

Every POST must say `Content-Type: application/json`, and one that carries an
Origin must come from this server's own address (Handler.post_refused, PW-1037):
any other web page open in the browser can't start jobs. (A cross-site JSON POST
needs a preflight, which this server never answers.)

Files are never cached (runs get regenerated in place). Requests run on
threads (ThreadingHTTPServer), so a slow /api/highlights doesn't block file
serving. Zooms, time zooms and finished worlds run on the job queue, up to
--jobs at once, each in a worker process (parallel.Pool: separate processes
scale, threads in one process don't). Highlights that aren't cached yet are
computed in worker processes of their own (HIGHLIGHT_WORKERS at once, PW-261),
so they don't wait for the jobs or for each other. Job state is kept in
.jobs/<port>.json and survives a restart (api.Jobs).
"""

from __future__ import annotations

import gzip
import email.utils
import http.server
import json
import os
import re
import shutil
import threading
import webbrowser
import zlib
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from . import api, family, favourites, make, thumbs
from .zoom import fine as ZF
from . import parallel as P
from . import store as S

KIND_OF = {"runs": "run", "worlds": "world", "zooms": "zoom"}


def delete(path: str) -> int:
    """DELETE /<runs|worlds|zooms>/<id> -> HTTP status (204 done, 404 none, 400 bad path)."""
    m = re.fullmatch(r"/(runs|worlds|zooms)/([0-9a-zA-Z_-]+?)(?:\.json)?", path)
    if not m:
        return 400
    gone = S.delete(KIND_OF[m.group(1)], m.group(2))
    for p in (S.root() / thumbs.CACHE).glob(f"{KIND_OF[m.group(1)]}-{m.group(2)}-*.png"):
        p.unlink(missing_ok=True)
    return 204 if gone else 404


def make_query(query: str) -> dict:
    """GET /api/make/estimate's query string as a make request (?seed=&preset=&level=&myr=&kyr=&timezoom=1&zooms=4...)."""
    q = dict(parse_qsl(query))
    req = {k: q[k] for k in ("seed", "preset", "level", "myr", "kyr", "zooms", "now", "tries", "peoples", "language_workers") if q.get(k) not in (None, "")}
    for k in ("timezoom", "finish", "highlights", "require_ice", "languages"):  # (languages: PW-1634)
        if k in q:
            req[k] = q[k] not in ("0", "false", "")
    return req


def make_estimate(query: str) -> tuple[dict, int]:
    try:
        spec = make.parse_make_request(make_query(query))
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    return {"spec": spec, **make.estimate(spec)}, 200


def active_job(jobs: api.Jobs | None, query: str) -> dict:
    """GET /api/jobs?type=refine: {"active": the queued or running job of that type (its id, label fields and
    progress), or None}. The viewer asks on load, so a refine started in another page shows its progress (PW-1438)."""
    jid = jobs.active(dict(parse_qsl(query)).get("type", "")) if jobs else None
    return {"active": jobs.get(jid) if jid else None}


def sections_list(query: str) -> tuple[dict, int]:
    """GET /api/sections?world=<id>: api.sections_listing, or an error."""
    world = dict(parse_qsl(query)).get("world", "").removesuffix(".json")
    if not world:
        return {"error": "give ?world=<id>"}, 400
    try:
        return api.sections_listing(world), 200
    except SystemExit as e:
        return {"error": str(e)}, 404


def refine_estimate(jobs: api.Jobs | None, query: str) -> tuple[dict, int]:
    """GET /api/refine/estimate?world=&level=: api.refine_estimate, with the refine already queued or running."""
    try:
        return api.refine_estimate(dict(parse_qsl(query)), busy=jobs.active("refine") if jobs else None), 200
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404


def highlights(query: str, compute=None) -> tuple[dict, int]:
    """GET /api/highlights?...: (JSON body, status). Synchronous: a few
    seconds at L6 (building a world from a keyframe), longer at L7/L8.
    compute: where what isn't cached is computed (api.highlights)."""
    q = dict(parse_qsl(query))
    try:
        return api.highlights(q, cached_only=q.get("cached") == "1", refresh=q.get("refresh") == "1",
                              compute=compute), 200
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run / world
        return {"error": str(e)}, 404
    except Exception as e:  # a bug: show it in the viewer rather than drop the connection
        return {"error": f"{type(e).__name__}: {e}"}, 500


def rename_landmass(raw: bytes) -> tuple[dict, int]:
    """POST /api/names {world, letter, name}: your own name for a landmass of a world (an empty name: back to the generated one), kept in
    worlds/names/<id>.json like `planet name`. Answers {names: [{letter, name, generated, custom}]} (PW-886)."""
    from . import names as NM
    try:
        b = json.loads(raw or b"{}")
        return {"names": NM.set_name(str(b.get("world") or ""), str(b.get("letter") or ""), str(b.get("name") or ""))}, 200
    except (ValueError, TypeError) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404


def presence_frame(query: str) -> tuple[bytes | dict, int]:
    """GET /api/presence?run=<id>&frame=<f>: one frame of the run's presence table and demes_all (PW-1269), so the viewer's
    "whose demes" picker downloads that frame's slice instead of the whole table. The body is binary: (lines + 1) uint32 offsets
    of each line's entries within the slice, then the cell ids (meta.presence.dtypes.cells), then the demes (uint16, if the
    run has demes_all). The entry count is the last offset."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import output as LO
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        meta = (json.loads((d / "run.json").read_text()).get("meta") or {})
        cells, dem, offs = LO.read_presence_frame(d, meta, int(q.get("frame", "")))
        return offs.astype("<u4").tobytes() + cells.tobytes() + dem.tobytes(), 200
    except (ValueError, IndexError) as e:
        return {"error": str(e)}, 400
    except KeyError as e:
        return {"error": e.args[0]}, 404
    except SystemExit as e:
        return {"error": str(e)}, 404


def favourites_list(query: str) -> tuple[dict, int]:
    """GET /api/favourites[?kind=]: the starred runs, worlds and zooms that still exist, oldest star first."""
    kind = dict(parse_qsl(query)).get("kind") or None
    if kind and kind not in S.KINDS:
        return {"error": f"unknown kind {kind!r}; one of {list(S.KINDS)}"}, 400
    return {"favourites": favourites.listing(kind)}, 200


def favourites_set(raw: bytes) -> tuple[dict, int]:
    """POST /api/favourites {kind, id, starred}: star (default) or unstar one item (an id may carry .json)."""
    try:
        b = json.loads(raw or b"{}")
        item_id = str(b.get("id") or "").removesuffix(".json")
        return {"favourites": favourites.set_favourite(str(b.get("kind") or ""), item_id, bool(b.get("starred", True)))}, 200
    except (ValueError, TypeError, AttributeError) as e:
        return {"error": str(e)}, 400
    except KeyError as e:
        return {"error": e.args[0]}, 404


def landmass_names(query: str) -> tuple[dict, int]:
    """GET /api/names?world=<id>: [{letter, name, generated, custom}] of a world's landmasses, as the viewer's labels and peoples runs show them."""
    from . import names as NM
    try:
        wid, _h, lms, gen = NM.world_landmasses(dict(parse_qsl(query)).get("world", ""))
        ov = NM.load_overrides(wid)
        return {"names": [{"letter": NM.rank_letter(i), "name": ov.get(NM.rank_letter(i), g), "generated": g, "custom": NM.rank_letter(i) in ov}
                          for i, g in enumerate(gen)]}, 200
    except SystemExit as e:
        return {"error": str(e)}, 404


_SPEAK_CACHE: dict = {}
_SPEAK_LOCK = threading.Lock()
SPEAK_CACHE_MAX = 512
SPEAK_MAX_CHARS = 200
SPEAK_MAX_SENTENCE_CHARS = 480   # (a sentence of up to 16 words; tone letters make tonal IPA long)


def speak_backends() -> tuple[dict, int]:
    """GET /api/speak/backends: which speech backends this server has, and the one 'auto' uses."""
    try:
        from .language import speak as SP
        have = SP.available_backends()
    except Exception as e:  # noqa: BLE001
        return {"backends": [], "default": None, "error": f"{type(e).__name__}: {e}"}, 200
    return {"backends": have, "default": "piper" if "piper" in have else ("espeak" if "espeak" in have else None)}, 200


def speak(query: str) -> tuple[bytes | dict, int]:
    """GET /api/speak?ipa=<IPA>&people=<lineage id>[&backend=][&sentence=1[&q=1]]: the word rendered as WAV by
    language/speak.py (the people's voice profile sets register and rate; at most 1 s of audio per word), or with sentence=1
    the whole sentence (speak_utterance: word gaps, declination and a final fall, or a final rise with q=1; capped at 16 words
    and 9 s). Cached in memory by (ipa, people, backend, sentence, q)."""
    q = dict(parse_qsl(query))
    ipa, people, backend = (q.get("ipa") or "").strip(), q.get("people") or None, q.get("backend") or "auto"
    sentence, question = q.get("sentence") in ("1", "true"), q.get("q") in ("1", "true")
    if not ipa:
        return {"error": "ipa= is required"}, 400
    if q.get("stress") in ("initial", "penult", "final", "antepenult", "weight"):  # the lect's fixed stress: marked, so it is heard
        from .language.inventory import stressed_ipa
        ipa = stressed_ipa(ipa, q["stress"])
    cap = SPEAK_MAX_SENTENCE_CHARS if sentence else SPEAK_MAX_CHARS
    if len(ipa) > cap:
        return {"error": f"ipa= is longer than {cap} characters"}, 400
    key = (ipa, people, backend, sentence, question)
    with _SPEAK_LOCK:
        if key in _SPEAK_CACHE:
            return _SPEAK_CACHE[key], 200
    try:
        from .language import speak as SP
        if sentence:
            b = SP.speak_utterance(ipa, SP.profile_for_people(people), backend=backend, question=question)
        else:
            b = SP.speak(ipa, SP.profile_for_people(people), backend=backend)
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:  # a missing backend (SP.BackendUnavailable) or a synthesis failure
        return {"error": f"{type(e).__name__}: {e}"}, 503
    with _SPEAK_LOCK:
        if len(_SPEAK_CACHE) >= SPEAK_CACHE_MAX:
            _SPEAK_CACHE.pop(next(iter(_SPEAK_CACHE)))
        _SPEAK_CACHE[key] = b
    return b, 200


def brief(query: str) -> tuple[dict, int]:
    """GET /api/brief?run=<run>&people=<id>|culture=<id>[&era=<kyr ago>][&calendar=<id>] or &region=lat,lon[,radius_km]: the culinary brief
    (lineages/brief.py, PW-728) as {markdown, brief} (PW-837: the viewer's Peoples panel shows it)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import brief as BR, readout as RO
        run, era = q.get("run"), float(q.get("era") or 0.0)
        if not run:
            raise ValueError("run= is required")
        region = None
        if q.get("region"):
            v = [float(x) for x in q["region"].split(",")]
            if len(v) not in (2, 3):
                raise ValueError("region=lat,lon[,radius_km]")
            region = (v[0], v[1], v[2] if len(v) == 3 else BR.DEFAULT_RADIUS_KM)
        culture = int(q["culture"]) if q.get("culture") not in (None, "") else None
        if region is None and culture is None and not q.get("people"):
            raise ValueError("give people=<id>, culture=<id> or region=lat,lon[,radius_km]")
        cal = None
        if q.get("calendar") not in (None, ""):  # (PW-1435: its dates in a culture's calendar; "X years ago" without)
            from .lineages import calendars as CA
            cal = CA.calendar_of(calendars_doc(S.find_run(run)), q["calendar"])
            if cal is None:
                raise ValueError(f"no calendar {q['calendar']} in this run")
        from .lineages.years import in_calendar
        with in_calendar(cal):
            b = RO.build(run, region=None if culture is not None else region, people=None if culture is not None else q.get("people"), era_kyr=era, culture=culture)
            md = BR.markdown(b)
        return {"markdown": md, "brief": b, "calendar": None if cal is None else {"id": cal["id"], "name": cal["name"]}}, 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run / people
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_cultures_cache: dict = {}  # (run id, run.json mtime) -> cultures doc: a run without cultures.json, worked out once per change


def cultures(query: str) -> tuple[dict, int]:
    """GET /api/cultures?run=<id>: the emergent cultures of a peoples run (lineages/cultures.py, PW-670) for the workbench's Cultures
    tab: the run's cultures.json if it has one, else derived from its demes (a few seconds) and kept in memory, never written into the run."""
    q = dict(parse_qsl(query))
    try:
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        if not (d / "cultures.json").exists():
            run = json.loads((d / "run.json").read_text())
            if not (run.get("meta") or {}).get("demes"):
                return {"error": "this run has no demes (older than PW-981): run the peoples again"}, 404
        return named_cultures(d), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


def _mtime(f: Path) -> float:
    return f.stat().st_mtime if f.exists() else 0.0


_lang_cache: dict = {}  # (run id, languages.json mtime) -> languages.json main file (names, PW-972), or None


def languages_main(d: Path) -> dict | None:
    """A run's languages.json without its sidecars (the names block is in the main file), None where it has none; kept in memory."""
    f = d / "languages.json"
    key = (d.name, _mtime(f))
    if key not in _lang_cache:
        from .language import output as LO
        _lang_cache.clear()
        _lang_cache[key] = LO.load(f, sidecars=False) if f.exists() else None
    return _lang_cache[key]


def named_cultures(d: Path) -> dict:
    """A run's cultures doc with the names slot filled (lineages/nameslot.py, PW-1436: the languages' names, else the PW-1249 gloss
    names): its cultures.json, else derived from its demes (a few seconds); kept in memory, never written into the run."""
    from .lineages import cultures as CU, nameslot as NS
    key = (d.name, _mtime(d / "run.json"), _mtime(d / "cultures.json"), _mtime(d / "languages.json"))
    if key not in _cultures_cache:
        f = d / "cultures.json"
        doc = json.loads(f.read_text()) if f.exists() else CU.derive(d)["doc"]
        meta = json.loads((d / "run.json").read_text()).get("meta") or {}
        NS.apply_cultures(doc, meta.get("lineages") or [], languages_main(d), NS.deme_cells(d))
        _cultures_cache.clear()
        _cultures_cache[key] = doc
    return _cultures_cache[key]


_calendars_cache: dict = {}  # (run id, mtimes, authored keys, version) -> calendars doc (PW-1435)


def calendars_doc(d: Path) -> dict:
    """A run's calendars (lineages/calendars.py, PW-1435), read from its named cultures, faiths, states, incursions and settlement
    ledger; kept in memory. Without a polities doc (no settlements.json) the states give none."""
    from .lineages import calendars as CA, nameslot as NS
    key = (d.name, _mtime(d / "run.json"), _mtime(d / "cultures.json"), _mtime(d / "languages.json"), _authored_key(d),
           _authored_key(d, "invasions"), CA.VERSION)
    if key not in _calendars_cache:
        meta = json.loads((d / "run.json").read_text()).get("meta") or {}
        C = named_cultures(d)["cultures"]
        try:
            gd = NS.apply_faiths(gods_doc(d), C)
        except (SystemExit, FileNotFoundError, KeyError):
            gd = None
        has_sites = (d / "settlements.json").exists()
        pd = NS.apply_polities(polities_doc(d), languages_main(d), C) if has_sites else None
        sites = json.loads((d / "settlements.json").read_text()).get("sites") if has_sites else None
        _calendars_cache.clear()
        _calendars_cache[key] = CA.derive(C, meta, gods=gd, polities=pd, sites=sites, place_names=NS.place_names(languages_main(d)))
    return _calendars_cache[key]


def calendars(query: str) -> tuple[dict, int]:
    """GET /api/calendars?run=<id>: the calendars a peoples run's cultures founded (PW-1435): {calendars: [{id, name, epoch_kyr, kind,
    event, culture, holders, alive, ended_kyr, p, fade}], by_culture, counts, rule, sources}. The viewer's "dates in" picker."""
    q = dict(parse_qsl(query))
    try:
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        if json.loads((d / "run.json").read_text()).get("meta", {}).get("kind") != "peoples":
            raise ValueError("calendars are read from a peoples run")
        if not (d / "cultures.json").exists():
            return {"error": "this run has no cultures (it is older than PW-670): run the peoples again"}, 404
        return calendars_doc(d), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_gods_cache: dict = {}  # (run id, run.json mtime, mode, authored.json mtime) -> gods doc
_inputs_cache: dict = {}  # (run id, run.json mtime) -> gods.inputs (the slow part: the land per culture per frame, ~25 s at L7)
_gods_lock = threading.Lock()  # (the gods, taboos and map requests come together: one derive, not three)


GODS_DIR = ".godscache"


def _authored_key(d: Path, part: str = "gods") -> str:
    """A run's authored.json as a short content hash ('' when it has nothing for that part): part "gods" (the gods mode and faiths: it
    keys every cache of the gods and taboos) or "invasions" (the invasions you schedule: it keys the polities doc, PW-1433, and the
    gods, whose rulers push their faith, PW-1477), so an edited faith never remakes the polities."""
    import hashlib
    from .lineages import gods as GD
    if not (d / GD.AUTHORED_FILE).exists():
        return ""
    A = GD.read_authored(d)
    v = A["invasions"] if part == "invasions" else [A["gods_mode"], A["faiths"]]
    if v in ([], [None, []]):
        return ""
    return hashlib.sha1(json.dumps(v, sort_keys=True).encode()).hexdigest()[:16]


def disk_cached(kind: str, d: Path, key: tuple, make):
    """A derived doc of run d kept on disk under <data root>/.godscache (never in the run folder): one file per (kind, run), holding the
    key it was made for (run id, run.json mtime, mode, authored hash) so a changed run or edit makes it again. make(): the doc."""
    import hashlib
    k = json.dumps([str(x) for x in key])
    f = S.root() / GODS_DIR / f"{kind}-{d.name}.json"
    try:
        doc = json.loads(f.read_text())
        if isinstance(doc, dict) and doc.get("_cache_key") == k:
            return doc["doc"]
    except (OSError, ValueError):
        pass
    out = make()
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        S.write_atomic(f, json.dumps({"_cache_key": k, "_hash": hashlib.sha1(k.encode()).hexdigest()[:8], "doc": out}, separators=(",", ":")))
    except OSError:
        pass  # (a read-only data root: memory only)
    return out


def gods_doc(d: Path, mode: str | None = None) -> dict:
    """A run's gods doc. mode: asked for, else the run's saved one (authored.json, PW-1309), else faith_made. Its gods.json when it is in
    this mode, has faiths (made since PW-1358) and no faiths are written in; else replayed from the run's inputs (kept in memory, so a
    new mode or an edited faith takes seconds) with its authored faiths (PW-1430)."""
    from .lineages import gods as GD
    A = GD.read_authored(d)
    meta_mode = (json.loads((d / "run.json").read_text()).get("meta") or {}).get("gods_mode")  # (chosen where the run was made, PW-1309)
    mode = mode or A["gods_mode"] or meta_mode or GD.MODE_DEFAULT
    f = d / "gods.json"
    if f.exists() and not A["faiths"]:
        doc = json.loads(f.read_text())
        if doc.get("gods_mode") == mode and doc.get("format") == GD.GODS_FORMAT:  # (an older gods.json lacks what the viewer reads: replayed)
            return doc
    if not (d / "cultures.json").exists():
        raise SystemExit("this run has no cultures (it is older than PW-670): run the peoples again")
    rk = (d.name, (d / "run.json").stat().st_mtime)
    key = (*rk, mode, GD.GODS_FORMAT, _authored_key(d), _authored_key(d, "invasions"))  # (the invasions too: rulers push their faith, PW-1477)
    with _gods_lock:
        if key not in _gods_cache:
            def make():
                if rk not in _inputs_cache:
                    _inputs_cache.clear()
                    _inputs_cache[rk] = GD.inputs(d)
                inp = _inputs_cache[rk]
                rule = GD.rule_table(polities_doc(d), inp["C"], inp["frames"]) if (d / "settlements.json").exists() else None
                return GD.replay(inp, mode, A["faiths"], rule)
            _gods_cache.clear()
            _gods_cache[key] = disk_cached(f"gods-{mode}", d, key, make)
        return _gods_cache[key]


def _authored_context(d: Path) -> tuple[int, set]:
    """(how many cultures, the people ids) of a run: what an authored faith may name."""
    if not (d / "cultures.json").exists():
        raise SystemExit("this run has no cultures (it is older than PW-670): run the peoples again")
    meta = json.loads((d / "run.json").read_text()).get("meta") or {}
    n = len(json.loads((d / "cultures.json").read_text()).get("cultures") or [])
    return n, {l["id"] for l in meta.get("lineages") or []}


def _authored_choices(d: Path) -> dict:
    """What an invasion row may name (PW-1433): the run's peoples {id, name} and its cultures {uid, name, people, born_kyr, ended_kyr}
    (cultures keyed by their cultures.json uid, PW-1283, rebuilt from the demes for an older file)."""
    from .lineages import cultures as CU
    meta = json.loads((d / "run.json").read_text()).get("meta") or {}
    C = json.loads((d / "cultures.json").read_text()) if (d / "cultures.json").exists() else {"cultures": []}
    dm = (meta.get("demes") or {}).get("file")
    try:
        uids = CU.uids(C, json.loads((d / dm).read_text())) if dm and (d / dm).exists() else [c.get("uid") for c in C["cultures"]]
    except (KeyError, IndexError, ValueError, TypeError):
        uids = [c.get("uid") for c in C["cultures"]]
    cul = [{"uid": u, "name": c.get("name"), "people": c.get("people"), "born_kyr": c.get("born_kyr"), "ended_kyr": c.get("ended_kyr")}
           for c, u in zip(C["cultures"], uids) if u]
    return {"peoples": [{"id": l["id"], "name": l.get("name") or l["id"]} for l in meta.get("lineages") or []], "cultures": cul}


def authored_get(query: str) -> tuple[dict, int]:
    """GET /api/authored?run=<id>: the run's authored.json ({format, gods_mode, faiths}; empty when it has none)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import gods as GD
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        out = GD.read_authored(d)
        if q.get("choices"):
            out["choices"] = _authored_choices(d)
        return out, 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404


def authored_set(raw: bytes) -> tuple[dict, int]:
    """POST /api/authored {run, faiths: [...], gods_mode}: check the faiths (gods.clean_authored, strict: the first problem answers 400)
    and save them as the run's authored.json; answers {saved, authored}. The viewer then fetches /api/gods and /api/taboos again."""
    try:
        from .lineages import gods as GD
        b = json.loads(raw or b"{}")
        if not isinstance(b, dict) or not b.get("run"):
            raise ValueError("run is required")
        d = S.find_run(str(b["run"]))
        n, peoples = _authored_context(d)
        old = GD.read_authored(d)
        mode = b.get("gods_mode", old["gods_mode"]) or None
        faiths = b["faiths"] if "faiths" in b else old["faiths"]
        saved = GD.write_authored(d, faiths, mode, n, peoples, b.get("invasions") if "invasions" in b else None)
        return {"saved": len(saved["faiths"]), "invasions": len(saved["invasions"]), "authored": saved}, 200
    except (ValueError, TypeError, AttributeError) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404


_taboos_cache: dict = {}


def taboos_doc(d: Path, mode: str | None = None) -> dict:
    """A run's taboos doc: its taboos.json when it has every kind (format procgen-taboos/2, PW-1311) and no faith is written in, else worked
    out from its gods doc (authored faiths and saved mode included, PW-1430) and cached in memory and on disk. Shared with the culinary brief."""
    from .lineages import taboos as TB
    from .lineages import gods as GD
    f = d / "taboos.json"
    if f.exists() and not GD.read_authored(d)["faiths"]:  # (faiths written in: their gods' taboos too, PW-1430)
        doc = json.loads(f.read_text())
        if doc.get("format") == "procgen-taboos/2":
            return doc
    gd = gods_doc(d, mode)
    key = (d.name, (d / "run.json").stat().st_mtime, gd.get("gods_mode"), _authored_key(d))
    if key not in _taboos_cache:
        _taboos_cache.clear()
        _taboos_cache[key] = disk_cached(f"taboos-{gd.get('gods_mode')}", d, key, lambda: TB.derive(d, gd))
    return _taboos_cache[key]


def taboos(query: str) -> tuple[dict, int]:
    """GET /api/taboos?run=<id>: the run's taboos.json when it has every kind (format procgen-taboos/2, PW-1311), else worked out from
    its gods doc and kept in memory, never written into the run."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import taboos as TB
        if not q.get("run"):
            raise ValueError("run= is required")
        return taboos_doc(S.find_run(q["run"]), q.get("mode")), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


def faithmap(query: str) -> tuple[bytes | dict, int]:
    """GET /api/faithmap?run=<id>&frame=<f>[&w=512|1024|2048]: the faiths at one stored frame as an equirectangular PNG (faithmap.py)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import faithmap_png as FM
        d = S.find_run(q.get("run", ""))
        w = int(q.get("w", 1024))
        if w not in (512, 1024, 2048):
            raise ValueError("w must be 512, 1024 or 2048")
        from . import api
        with api.COMPUTE:  # (the grid lookup is a parallel numba kernel: one at a time per process, as thumbs)
            only = int(q["only"]) if q.get("only", "").isdigit() else None
            return FM.render(d, gods_doc(d), int(q.get("frame", 0)), w, only), 200
    except (ValueError, IndexError, KeyError) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_polities_cache: dict = {}  # (run id, run.json mtime, version) -> polities doc
_polities_lock = threading.Lock()  # (the summary and the first map come together: one derive)


def polities_doc(d: Path) -> dict:
    """A run's polities doc (lineages/polities.py, PW-1431): read after the run from its settlements, techs, cultures and presence
    (~30 s at L7), kept in memory and on disk under <data root>/.godscache, never in the run folder."""
    from .lineages import polities as PO
    from .lineages import gods as GD
    from .lineages import invasions as IV
    inv = _authored_key(d, "invasions")
    key = (d.name, (d / "run.json").stat().st_mtime, PO.VERSION, inv) + ((IV.VERSION,) if inv else ())  # (an edited invasion remakes
    # it, PW-1433; so does a change in what a row does, IV.VERSION, PW-1450, and only for a run with rows)
    if (d / "polities_live.json").exists():  # (PW-1575: the read-out draws the history's polities: their format is part of the key)
        from .lineages.history import polity_live as PLV
        key += (PLV.FORMAT, PO._LIVE_READ)
    with _polities_lock:
        if key not in _polities_cache:
            _polities_cache.clear()
            _polities_cache[key] = disk_cached("polities", d, key, lambda: PO.derive(d, invasions=GD.read_authored(d)["invasions"]))
        return _polities_cache[key]


def polities(query: str) -> tuple[dict, int]:
    """GET /api/polities?run=<id>[&ago=<kyr ago>]: a peoples run's chiefdoms, states, empires and dragon realms (lineages/polities.py,
    PW-1431). Without ago: the polities (the state cards), the cultures they name (by uid) and each century step's counts; with ago:
    the nearest step's map ({step, ago, polities: [{id, tier, cells, subjects, people}]})."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import polities as PO
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        if json.loads((d / "run.json").read_text()).get("meta", {}).get("kind") != "peoples":
            raise ValueError("polities are read from a peoples run")
        doc = polities_doc(d)
        if q.get("ago") not in (None, ""):
            return PO.step_view(doc, float(q["ago"])), 200
        from .lineages import nameslot as NS
        return NS.apply_polities(PO.summary(doc), languages_main(d), named_cultures(d)["cultures"]), 200  # (the names slot, PW-1436)
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_trade_cache: dict = {}  # (run id, run.json mtime, version) -> goods ledger doc
_trade_lock = threading.Lock()


def trade_doc(d: Path) -> dict:
    """A run's goods ledger (lineages/trade.py, PW-1502): read after the run from its land-use window, cultures, crops, herds, techs and
    the world's goods (~10 s at L7), kept in memory and on disk under <data root>/.godscache, never in the run folder."""
    from .lineages import trade as TR
    key = (d.name, (d / "run.json").stat().st_mtime, TR.VERSION)
    with _trade_lock:
        if key not in _trade_cache:
            _trade_cache.clear()
            _trade_cache[key] = disk_cached("trade", d, key, lambda: TR.derive(d))
        return _trade_cache[key]


_trade_flow_cache: dict = {}  # (run id, run.json mtime, versions, authored keys) -> exchange doc
_trade_flow_lock = threading.Lock()


def trade_flow_doc(d: Path) -> dict:
    """A run's exchange (lineages/trade_flow.py, PW-1503): goods moving between neighbours, read after the run from the goods ledger, the
    world's rivers and coasts, the techs, the polities' wars (polities_doc) and the cultures' tolerance (the gods doc's attitudes); a
    minute or two at L7 the first time, kept in memory and on disk under <data root>/.godscache, never in the run folder."""
    from .lineages import trade as TR
    from .lineages import trade_flow as TF
    key = (d.name, (d / "run.json").stat().st_mtime, TF.VERSION, TR.VERSION, _authored_key(d, "invasions"), _authored_key(d))
    with _trade_flow_lock:
        if key not in _trade_flow_cache:
            def make():
                try:
                    pol = polities_doc(d)
                except Exception:  # (a run without settlements has no polities: no border is closed by war)
                    pol = None
                try:
                    att = gods_doc(d).get("attitudes")
                except Exception:
                    att = None
                return TF.derive(d, pol=pol, att=att)
            _trade_flow_cache.clear()
            _trade_flow_cache[key] = disk_cached("tradeflow", d, key, make)
        return _trade_flow_cache[key]


_tongues_cache: dict = {}  # (run id, run.json mtime, versions, authored keys, languages.json mtime) -> tongues ledger
_tongues_lock = threading.Lock()


def tongues_doc(d: Path) -> dict:
    """A run's tongues ledger (lineages/tongues.py, PW-1526): per culture and era the tongues its people speak besides its own (a
    neighbour's, a ruler's, a host's, a trade language or pidgin, a liturgy), read after the run from the exchange doc (trade_flow_doc),
    the polities, the gods doc and languages.json; kept in memory and on disk under <data root>/.godscache, never in the run folder."""
    from .lineages import trade as TR
    from .lineages import trade_flow as TF
    from .lineages import tongues as TG
    lf = d / "languages.json"
    key = (d.name, (d / "run.json").stat().st_mtime, TG.VERSION, TF.VERSION, TR.VERSION, _authored_key(d, "invasions"), _authored_key(d),
           lf.stat().st_mtime if lf.exists() else None)
    with _tongues_lock:
        if key not in _tongues_cache:
            def make():
                try:
                    pol = polities_doc(d)
                except Exception:  # (a run without settlements has no polities: nobody rules anybody)
                    pol = None
                try:
                    gods = gods_doc(d)
                except Exception:
                    gods = None
                return TG.derive(d, trade_flow_doc(d), pol=pol, gods=gods)
            _tongues_cache.clear()
            _tongues_cache[key] = disk_cached("tongues", d, key, make)
        return _tongues_cache[key]


def tongues(query: str) -> tuple[dict, int]:
    """GET /api/tongues?run=<id>[&culture=<id>|&ago=<kyr>]: a peoples run's tongues ledger (lineages/tongues.py, PW-1526). Without
    culture or ago: per era the counts and the trade languages (tongues.summary); with culture: that culture's other tongues per era;
    with ago: the era nearest it whole (every culture's rows and the trade languages)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import tongues as TG
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        meta = json.loads((d / "run.json").read_text()).get("meta", {})
        if meta.get("kind") != "peoples" or not meta.get("eraq") or not meta.get("world"):
            raise ValueError("the tongues ledger is read from a peoples run with a land-use window and a world")
        doc = tongues_doc(d)
        if q.get("culture") not in (None, ""):
            c = int(q["culture"])
            if not 0 <= c < len(doc["cultures"]):
                raise ValueError(f"no culture {c} in this run")
            return {"culture": c, "columns": doc["columns"], "rows": TG.culture_view(doc, c)}, 200
        if q.get("ago") not in (None, ""):
            fs = doc["frames"]
            if not fs:
                return {"ago_kyr": None, "cultures": {}, "trade_languages": []}, 200
            a = float(q["ago"])
            f = min(fs, key=lambda f: abs(f["ago_kyr"] - a))
            return {"columns": doc["columns"], "names": [x["name"] for x in doc["cultures"]], **f}, 200
        return TG.summary(doc), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


def trade(query: str) -> tuple[dict, int]:
    """GET /api/trade?run=<id>[&culture=<id>[&flows=1]]: a peoples run's goods ledger (lineages/trade.py, PW-1502). Without culture: per way
    of life, the goods most often in surplus and lacking, and the frames; with culture: that culture's surplus and lacks at each frame of the
    land-use window (the last ~12.5 kyr), its "has / lacks" line, and what every good is made from; with flows=1 instead: per frame where
    each good it lacks comes from, where each good it spares goes, and its trading partners (lineages/trade_flow.py, PW-1503)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import trade as TR
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        meta = json.loads((d / "run.json").read_text()).get("meta", {})
        if meta.get("kind") != "peoples":
            raise ValueError("the goods ledger is read from a peoples run")
        if not meta.get("eraq") or not meta.get("world"):
            raise ValueError("this run has no land-use window or no world (made before PW-742): no goods ledger")
        doc = trade_doc(d)
        if q.get("routes"):  # (step 3, PW-1504: the routes and trading towns of the frame nearest ago, for the globe's Trade routes overlay)
            from .lineages import trade_routes as RT
            return RT.frame_view(trade_flow_doc(d), float(q.get("ago") or 0.0)), 200
        if q.get("culture") not in (None, "") and q.get("flows"):
            from .lineages import trade_flow as TF
            c = int(q["culture"])
            if not 0 <= c < len(doc["cultures"]):
                raise ValueError(f"no culture {c} in this run")
            fd = trade_flow_doc(d)
            return {"culture": c, "rows": TF.culture_view(fd, c, doc["cultures"]), "constants": fd["constants"], "seconds": fd["seconds"],
                    "had_polities": fd["had_polities"], "had_attitudes": fd["had_attitudes"]}, 200
        if q.get("culture") not in (None, ""):
            return TR.culture_view(doc, int(q["culture"])), 200
        return TR.summary(doc), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


_techspread_cache: dict = {}  # (run id, run.json mtime, version, tech) -> spread doc (a few seconds each; the last few kept)


def techspread(query: str) -> tuple[dict, int]:
    """GET /api/techspread?run=<id>[&tech=<tech id>]: how fast one tech (writing by default) spread through a peoples run
    (lineages/techspread.py): per people and per culture the date it first knew it and how, and the share of settled people and of
    town cells that knew it at each century step. Read from the run, never written into it."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import techspread as TS
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        tech = q.get("tech") or "writing"
        key = (d.name, (d / "run.json").stat().st_mtime, TS.VERSION, tech)
        if key not in _techspread_cache:
            if len(_techspread_cache) > 8:
                _techspread_cache.clear()
            _techspread_cache[key] = TS.derive(d, tech)
        return _techspread_cache[key], 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


def gods(query: str) -> tuple[dict, int]:
    """GET /api/gods?run=<id>[&mode=faith_made|belief_only|absolute]: the gods of a peoples run's cultures (lineages/gods.py, PW-1306): the
    run's gods.json if it has one (and no other mode is asked for), else worked out from its cultures (some seconds) and kept in memory,
    never written into the run. Needs cultures.json (a run older than PW-670 has none)."""
    q = dict(parse_qsl(query))
    try:
        from .lineages import gods as GD
        if not q.get("run"):
            raise ValueError("run= is required")
        d = S.find_run(q["run"])
        mode = q.get("mode") or None  # (none asked: the run's saved mode, authored.json, PW-1309)
        if mode is not None and mode not in GD.GODS_MODES:
            raise ValueError(f"mode must be one of {GD.GODS_MODES}")
        from .lineages import nameslot as NS
        return NS.apply_faiths(gods_doc(d, mode), named_cultures(d)["cultures"]), 200  # (the names slot, PW-1436)
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}, 500


# ---------------------------------------------------------------- /api/cell
CELL_INPUTS = ("temperature", "warm_month", "cold_month", "precipitation_jul", "precipitation_jan",
               "sunshine_jul", "sunshine_jan")  # what climate.months needs from a world (the light's shade)
CELL_WORLDS = 4  # worlds kept loaded (their CELL_INPUTS only: ~9 MB each at L7)
_cell_lock = threading.Lock()
_cell_worlds: dict = {}  # world id -> (file mtime, lat, tilt, {layer: array}), oldest first
_grid_lat: dict = {}  # level -> cell latitudes


def world_columns(path: Path, keys) -> dict:
    """{layer: float array} for some of a saved world's layers: only their files are read."""
    import numpy as np
    specs = json.loads(Path(path).read_text())["layers"]
    return {k: np.asarray(v, float) for k, v in S.read_world_layers(specs, list(keys)).items()}


def cell(query: str) -> tuple[dict, int]:
    """GET /api/cell?world=<id>&i=<cell>: (JSON body, status). The cell's
    twelve months, Jan..Dec, from climate.months (PW-194) on the world's
    stored climate: t (C) and p (mm in the month). Only the one cell is
    computed; the world's inputs stay loaded for the next cell (~1 s to read
    an L7 world and its grid the first time, ~1 ms after)."""
    from . import climate
    from .grid import build_grid
    q = dict(parse_qsl(query))
    wid = q.get("world", "").removesuffix(".json")
    if not S.exists("world", wid):
        return {"error": f"no world {wid!r}"}, 404
    try:
        i = int(q.get("i", ""))
    except ValueError:
        return {"error": "i: a cell index"}, 400
    path = S.path_of("world", wid)
    mtime = path.stat().st_mtime_ns
    with _cell_lock:
        w = _cell_worlds.pop(wid, None)
        if w is None or w[0] != mtime:  # (a world rebuilt in place is read again)
            meta = S.read_header(path, ("meta",))["meta"]
            if meta["level"] not in _grid_lat:
                _grid_lat[meta["level"]] = build_grid(meta["level"]).lat
            w = (mtime, _grid_lat[meta["level"]], meta.get("params", {}).get("tilt", 23.4),
                 world_columns(path, CELL_INPUTS))
        _cell_worlds[wid] = w  # (now the newest)
        while len(_cell_worlds) > CELL_WORLDS:
            del _cell_worlds[next(iter(_cell_worlds))]
    _, lat, tilt, L = w
    if not 0 <= i < len(lat):
        return {"error": f"i: 0..{len(lat) - 1}"}, 400
    c = {k: v[i:i + 1] for k, v in L.items()}
    sh_jul, sh_jan = climate.shade_from_hours(lat[i:i + 1], c["sunshine_jul"], c["sunshine_jan"], tilt)
    mo = climate.months(lat[i:i + 1], c["temperature"], c["warm_month"], c["cold_month"], c["precipitation_jul"],
                        c["precipitation_jan"], tilt, sh_jul, sh_jan)
    return {"world": wid, "i": i, "lat": round(float(lat[i]), 3),
            "t": [round(float(x), 2) for x in mo["t"][:, 0]], "p": [round(float(x), 2) for x in mo["p"][:, 0]]}, 200


# ---------------------------------------------------------------- gzip
GZIP_SUFFIXES = (".bin", ".json")  # run layers, worlds, grids, run.json
GZIP_MIN = 64 << 10  # smaller files go as they are (64 KB: an L7 world's one-byte layers, 160 KB, shrink 3-50x; PW-1209)
# level 1: an L7 run's default layers 330 -> ~87 MB, ~1.4 s for the biggest
# file (level 6: ~3% smaller, twice the time). An int16 elevation barely
# shrinks (78 -> 67 MB); the int8 and mostly-zero layers 5-50x.
GZIP_LEVEL = 1
GZIP_DIR = ".gzcache"


def gz_path(src: Path, st: os.stat_result) -> Path:
    """Where src's gzipped copy is cached: <data root>/.gzcache/<its path
    there>.<size>-<mtime>.gz (a file rewritten in place gets a new name)."""
    rel = os.path.relpath(src, S.root())
    return S.root() / GZIP_DIR / f"{rel}.{st.st_size}-{st.st_mtime_ns}.gz"


PRUNE_GZ_EVERY_S = 60.0
_pruned_at = [float("-inf")]


def prune_gz(force: bool = False) -> None:
    """Drop cached copies whose file is gone or has changed (deleted runs and
    worlds, regenerated layers). At most once a minute unless forced: it walks
    the whole cache, and a world's ~180 layer files are cached together (an L8
    world's first opening took 11 s with a walk after each; PW-1209)."""
    import time
    if not force and time.monotonic() - _pruned_at[0] < PRUNE_GZ_EVERY_S:
        return
    _pruned_at[0] = time.monotonic()
    top = S.root() / GZIP_DIR
    for p in top.rglob("*.gz"):
        src = S.root() / p.relative_to(top).parent / p.name.rsplit(".", 2)[0]
        try:
            ok = gz_path(src, src.stat()) == p
        except OSError:
            ok = False
        if not ok:
            p.unlink(missing_ok=True)


def etag(st: os.stat_result, gz: bool = False) -> str:
    """A data file's validator: its size and modification time (PW-1045). The gzipped answer is a
    different body, so it gets its own tag."""
    return f'"{st.st_size:x}-{st.st_mtime_ns:x}{"-gz" if gz else ""}"'


def etag_matches(header: str | None, tag: str) -> bool:
    """If-None-Match names tag (or *); weak tags (W/"...") count, as for a GET they should."""
    if not header:
        return False
    tags = [t.strip().removeprefix("W/") for t in header.split(",")]
    return "*" in tags or tag in tags


def accepts_gzip(header: str | None) -> bool:
    """Accept-Encoding names gzip (and not with q=0)."""
    for a in (header or "").split(","):
        name, *params = [x.strip() for x in a.split(";")]
        if name == "gzip":
            return not any(x.replace(" ", "") in ("q=0", "q=0.0", "q=0.00", "q=0.000") for x in params)
    return False


def submit(jobs: api.Jobs, path: str, body: bytes) -> tuple[dict, int]:
    """POST /api/zoom, /api/timezoom or /api/finish: checks the request now
    (so a bad one fails at once), then queues it."""
    try:
        req = json.loads(body or b"{}")
        if path == "/api/make":
            req = make.parse_make_request(req)
        elif path == "/api/zoom":
            req = api.parse_zoom_request(req)  # (normalised: the same zoom asked two ways is one job)
            if not api.existing_zoom(req):  # (a zoom already built costs nothing: no guard)
                # at most one section-sized zoom at a time (the identical request is the same job: Jobs.submit)
                busy = jobs.active_where(lambda q: q != req and "type" not in q and api.zoom_is_heavy(q))
                est = api.zoom_estimate(req, busy=busy)
                if est["refuse"]:
                    return {"error": "not started: " + "; ".join(est["refuse"]), "estimate": est}, 409
        elif path == "/api/highlight-zooms":
            req = api.parse_highlight_zooms_request(req)
        elif path == "/api/enrich":  # resource / coast layers added to a saved world
            req = api.parse_enrich_request(req)
        elif path == "/api/finish":  # kyr snaps to a frame, t to a keyframe
            req = api.parse_finish_request(req)
        elif path == "/api/refine":  # one at a time, and only with room for it (PW-1438)
            est = api.refine_estimate(req, busy=jobs.active("refine"))
            if est["refuse"]:
                return {"error": "not started: " + "; ".join(est["refuse"]), "estimate": est}, 409
            req = {**{k: est[k] for k in ("type", "world", "level")}, "estimate_min": est["minutes"]}  # (the viewer's ETA)
        else:  # t snaps to a keyframe
            req = api.parse_timezoom_request(req)
    except (ValueError, api.BadRequest) as e:
        return {"error": str(e)}, 400
    except SystemExit as e:  # no such run
        return {"error": str(e)}, 404
    return {"job": jobs.submit(req)}, 200


class Handler(http.server.SimpleHTTPRequestHandler):
    jobs: api.Jobs | None = None  # set by serve()
    hl_pool: P.Pool | None = None  # (highlights' worker processes, set by serve())

    def translate_path(self, path):
        # the viewer (and the review pages it links to, docs/review/, PW-967) comes from the repository, everything else from the data root
        parts = urlsplit(path).path.lstrip("/").split("/", 2)
        self.directory = str(S.REPO if parts[0] == "viewer" or parts[:2] == ["docs", "review"] else S.root())
        return super().translate_path(path)

    # Caching (PW-1045): the viewer's own files and every API answer are no-store (a code change shows on reload);
    # data files (runs, worlds, zooms, grids: up to ~100 MB a run) are no-cache with an ETag, so the browser keeps
    # its copy and asks again, and an unchanged file costs a 304 instead of a download.
    data_etag: str | None = None

    def end_headers(self):
        if self.data_etag:
            self.send_header("Cache-Control", "no-cache")
            self.send_header("ETag", self.data_etag)
            self.send_header("Vary", "Accept-Encoding")
            self.data_etag = None
        else:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def data_file(self) -> Path | None:
        """The data file this GET names (not the viewer, the review pages or the API), when it exists."""
        parts = urlsplit(self.path).path.lstrip("/").split("/")
        if parts[0] in ("viewer", "api") or parts[:2] == ["docs", "review"]:
            return None
        p = Path(self.translate_path(self.path))
        try:
            return p if p.is_file() else None
        except OSError:
            return None

    def not_modified(self, tag: str, mtime: float) -> bool:
        """Answer 304 when the browser's copy is this one: If-None-Match names the tag, or (with no If-None-Match)
        If-Modified-Since is not older than the file. This server speaks HTTP/1.0, and to a 1.0 server Chrome
        revalidates by date only, so both are needed."""
        inm, ims = self.headers.get("If-None-Match"), self.headers.get("If-Modified-Since")
        if inm is not None:
            fresh = etag_matches(inm, tag)
        else:
            try:
                fresh = ims is not None and int(mtime) <= email.utils.parsedate_to_datetime(ims).timestamp()
            except (TypeError, ValueError, IndexError, OverflowError):
                fresh = False
        if not fresh:
            return False
        self.send_response(304)
        self.data_etag = tag
        self.end_headers()
        return True

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_gzip(self, src: Path) -> None:
        """src gzipped: the cached copy, or compressed while it is sent (no
        Content-Length then: HTTP/1.0 closes the connection at the end) and
        cached for next time."""
        cache = gz_path(src, src.stat())
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(src)))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Last-Modified", self.date_time_string(src.stat().st_mtime))
        if cache.exists():
            self.send_header("Content-Length", str(cache.stat().st_size))
            self.end_headers()
            with open(cache, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return
        self.end_headers()
        cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache.with_name(f".{cache.name}.{threading.get_ident()}.tmp")
        try:
            with open(src, "rb") as f, open(tmp, "wb") as out:
                z = zlib.compressobj(GZIP_LEVEL, zlib.DEFLATED, 31)  # (31: with the gzip wrapper)
                while True:
                    chunk = f.read(1 << 20)
                    b = z.compress(chunk) if chunk else z.flush()
                    out.write(b)
                    self.wfile.write(b)
                    if not chunk:
                        break
            os.replace(tmp, cache)
        finally:
            tmp.unlink(missing_ok=True)
        for old in cache.parent.glob(f"{src.name}.*.gz"):  # (this file's older copies at once; the rest: prune_gz)
            if old != cache and old.name.rsplit(".", 2)[0] == src.name:
                old.unlink(missing_ok=True)
        prune_gz()

    def gzippable(self) -> Path | None:
        """The data file this GET asks for, when it should go gzipped."""
        top = urlsplit(self.path).path.lstrip("/").split("/", 1)[0]
        if top == "viewer" or not accepts_gzip(self.headers.get("Accept-Encoding")):
            return None
        p = Path(self.translate_path(self.path))
        try:
            ok = p.suffix in GZIP_SUFFIXES and p.is_file() and p.stat().st_size >= GZIP_MIN
        except OSError:
            ok = False
        return p if ok else None

    def do_GET(self):
        url = urlsplit(self.path)
        if self.lineages_api("GET"):
            return
        if url.path == "/api/highlights":
            return self.send_json(*highlights(url.query, self.hl_pool.call if self.hl_pool else None))
        if url.path == "/api/brief":
            return self.send_json(*brief(url.query))
        if url.path == "/api/speak/backends":
            return self.send_json(*speak_backends())
        if url.path == "/api/speak":
            body, code = speak(url.query)
            if isinstance(body, dict):
                return self.send_json(body, code)
            self.send_response(code)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if url.path == "/api/presence":
            body, code = presence_frame(url.query)
            if isinstance(body, dict):
                return self.send_json(body, code)
            self.send_response(code)
            self.send_header("Content-Type", "application/octet-stream")
            if accepts_gzip(self.headers.get("Accept-Encoding")):  # (cell ids ascend, so it gzips ~3.4x at L7)
                body = gzip.compress(body, 1)
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if url.path == "/api/cultures":
            return self.send_json(*cultures(url.query))
        if url.path == "/api/gods":
            return self.send_json(*gods(url.query))
        if url.path == "/api/calendars":
            return self.send_json(*calendars(url.query))
        if url.path == "/api/authored":
            return self.send_json(*authored_get(url.query))
        if url.path == "/api/taboos":
            return self.send_json(*taboos(url.query))
        if url.path == "/api/polities":
            return self.send_json(*polities(url.query))
        if url.path == "/api/techspread":
            return self.send_json(*techspread(url.query))
        if url.path == "/api/trade":
            return self.send_json(*trade(url.query))
        if url.path == "/api/tongues":
            return self.send_json(*tongues(url.query))
        if url.path == "/api/faithmap":
            body, code = faithmap(url.query)
            if isinstance(body, dict):
                return self.send_json(body, code)
            self.send_response(code)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if url.path == "/api/names":
            return self.send_json(*landmass_names(url.query))
        if url.path == "/api/favourites":
            return self.send_json(*favourites_list(url.query))
        if url.path == "/api/cell":
            return self.send_json(*cell(url.query))
        if url.path == "/api/fine-rules":  # what a fine zoom may be (zoom.fine): the viewer's size menu
            q = dict(parse_qsl(url.query))
            try:
                res = float(q["res_km"]) if "res_km" in q else None
            except ValueError:
                return self.send_json({"error": "res_km must be a number"}, 400)
            return self.send_json({**ZF.rules(), **({"sizes": ZF.size_options(res)} if res else {})})
        if url.path == "/api/sections":  # ?world=: the tiling's sections with what is built (api.sections_listing)
            return self.send_json(*sections_list(url.query))
        if url.path == "/api/planets":
            return self.send_json({"planets": family.planets()})
        if url.path == "/api/make/options":
            return self.send_json(make.options())
        if url.path == "/api/make/estimate":
            return self.send_json(*make_estimate(url.query))
        if url.path == "/api/refine/estimate":
            return self.send_json(*refine_estimate(self.jobs, url.query))
        if url.path == "/api/jobs":  # ?type=refine: the queued or running job of that type, so a page opened later follows it
            return self.send_json(active_job(self.jobs, url.query))
        if url.path == "/api/thumb":
            q = dict(parse_qsl(url.query))
            w = q.get("w", "")
            png = thumbs.thumb(q.get("kind", ""), q.get("id", ""), q.get("proj", "equal-earth"), int(w) if w.isdigit() else thumbs.W)
            if png is None:
                return self.send_error(404)
            body = png.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        gz = self.gzippable()
        if gz:
            st = gz.stat()
            tag = etag(st, gz=True)
            if self.not_modified(tag, st.st_mtime):
                return
            self.data_etag = tag
            return self.send_gzip(gz)
        m = re.fullmatch(r"/api/jobs/([0-9a-zA-Z_-]+)", url.path)
        if m:
            job = self.jobs.get(m.group(1))
            return self.send_json(job if job else {"error": "no such job"}, 200 if job else 404)
        f = self.data_file()
        if f:
            st = f.stat()
            tag = etag(st)
            if self.not_modified(tag, st.st_mtime):
                return
            self.data_etag = tag
        return super().do_GET()

    def lineages_api(self, method: str) -> bool:
        """The peoples editor (viewer/lineages.html, planet/lineages/): GET /api/lineage-schema (its option lists,
        lineages.run.editor_schema), GET /api/lineage-trees, GET or POST
        /api/lineage-tree?name=N (the tree as JSON; POST validates and saves it), POST /api/lineages
        {world | timezoom, tree | raw, tries} (queued on the job queue like a time zoom, ~20 s a try at L6;
        answers {job}; GET /api/jobs/<id> has its progress, and {run} when done)."""
        url = urlsplit(self.path)
        if not url.path.startswith("/api/lineage"):
            return False
        from .lineages import run as LR
        q = dict(parse_qsl(url.query))
        try:
            if method == "GET" and url.path == "/api/lineage-schema":
                self.send_json(LR.editor_schema())
            elif method == "GET" and url.path == "/api/lineage-trees":
                self.send_json({"trees": [{k: v for k, v in t.items() if k != "file"} for t in LR.list_trees()]})
            elif method == "GET" and url.path == "/api/lineage-tree":
                self.send_json(LR.read_raw(q.get("name", "")))
            elif method == "POST" and url.path in ("/api/lineage-tree", "/api/lineages"):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if url.path == "/api/lineage-tree":
                    LR.save_raw(q.get("name", ""), body)
                    self.send_json({"saved": q.get("name")})
                else:
                    try:
                        req = api.parse_lineages_request(body)
                    except api.BadRequest as e:
                        return self.send_json({"error": str(e)}, 400) or True
                    self.send_json({"job": self.jobs.submit(req)})
            else:
                self.send_error(404)
        except (ValueError, KeyError) as e:
            self.send_json({"error": str(e)}, 400)
        except (FileNotFoundError, SystemExit) as e:
            self.send_json({"error": str(e)}, 404)
        return True

    def post_refused(self) -> str | None:
        """Why this POST is refused, or None (PW-1037): it must be JSON, and an Origin, if sent,
        must be this server's own address (http://127.0.0.1:<port> or http://localhost:<port>)."""
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return "POST needs Content-Type: application/json"
        origin = self.headers.get("Origin")
        if origin is not None:
            port = self.server.server_address[1]
            if origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
                return f"cross-site POST refused (Origin {origin})"
        return None

    def do_POST(self):
        refused = self.post_refused()
        if refused:
            return self.send_json({"error": refused}, 403)
        if self.lineages_api("POST"):
            return
        if self.path == "/api/favourites":
            return self.send_json(*favourites_set(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
        if self.path == "/api/names":
            return self.send_json(*rename_landmass(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
        if self.path == "/api/authored":
            return self.send_json(*authored_set(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
        if self.path not in ("/api/zoom", "/api/timezoom", "/api/finish", "/api/make", "/api/highlight-zooms",
                         "/api/enrich", "/api/refine"):
            return self.send_error(404)
        self.send_json(*submit(self.jobs, self.path, self.rfile.read(int(self.headers.get("Content-Length", 0)))))

    def do_DELETE(self):
        m = re.fullmatch(r"/api/jobs/([0-9a-zA-Z_-]+)", urlsplit(self.path).path)
        if m:  # cancel a job
            out = self.jobs.cancel(m.group(1))
            return self.send_json(out if out else {"error": "no such job"}, 200 if out else 404)
        code = delete(self.path)
        if code == 400:
            return self.send_error(400, "expected /runs/<id>, /worlds/<id> or /zooms/<id>")
        self.send_response(code)
        self.end_headers()

    def log_message(self, *a):
        pass


JOBS = 4  # jobs at once (worker processes) by default
HIGHLIGHT_WORKERS = 2  # highlights computed at once (worker processes, started when first needed)


def serve(port: int = 8765, open_browser: bool = True, jobs: int = JOBS, threads: int | None = None):
    """jobs: how many jobs run at once, each in a worker process with
    `threads` numba threads (default: the cores shared out, at most 8)."""
    for kind in S.KINDS:
        S.update_index(kind)
    pool = P.Pool(jobs, threads)
    try:
        Handler.hl_pool = P.Pool(HIGHLIGHT_WORKERS, pool.threads)
        # job state survives a restart (per checkout and port: worktrees share the data folders)
        Handler.jobs = api.Jobs(pool.caller(api.any_job), S.REPO / ".jobs" / f"{port}.json", workers=jobs,
                                contexts=True)
        http.server.ThreadingHTTPServer.allow_reuse_address = True
        http.server.ThreadingHTTPServer.daemon_threads = True
        # a world's ~180 layer files are asked for at once, each on its own connection (HTTP/1.0): a deeper accept
        # queue than socketserver's default of 5, so a burst is not dropped and retried (PW-1209)
        http.server.ThreadingHTTPServer.request_queue_size = 256
        with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
            url = f"http://127.0.0.1:{port}/viewer/"
            print(f"Viewer at {url}   (data: {S.root()}; {jobs} jobs at once, {pool.threads} threads each; "
                  f"Ctrl-C to stop)", flush=True)
            if open_browser:
                webbrowser.open(url)
            httpd.serve_forever()
    finally:
        try:
            pool.close(kill=True)  # (running jobs are queued again at the next start)
        finally:
            if Handler.hl_pool:
                Handler.hl_pool.close(kill=True)
