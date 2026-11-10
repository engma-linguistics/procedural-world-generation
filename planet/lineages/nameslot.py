"""The names slot (PW-1436): every culture, faith, state and place carries one name field, `name`, that the brief and the viewer read.

Read-out only, like readout.py: nothing in the history or the stored docs is changed on disk. The slot is filled in this order:

1. **The languages' names** (planet/language/names.py, PW-972), where the run has a languages.json:
   - a culture: the endonym its largest living deme says (`names.demes[d].name`; every living lect of a people says its own form of
     the people's name, so sister cultures that speak apart are told apart). Two living cultures that would share a form take their
     deme's river or lake name ("Gnili of Gyerrihigyu"); a culture with no living deme keeps its gloss.
   - a place (a settlement of the ledger): its own name (`names.demes[d].settlements`, by site), with `english`, the Common's
     English rendering of its meaning (PW-1654, on by default in the viewer: PW-1655) and `local`, what the locals call it.
   - a state: its capital's name, composed as polities._name composes it ("Iligya (humans)"; a chiefdom "Chiefdom in Iligya (humans)";
     a dragon realm keeps "Realm of the ..."), numbered only where two states share a capital name.
   - a faith: composed as gods.faith_docs composes it ("the sky faith of <culture>"), with the culture's slot name; a faith you wrote
     keeps its own name.
2. **The gloss names** (PW-1249, `gloss_names`): what a culture is and where it began, made distinct without "(7)": a repeated
   name takes its founding date, then its way of life now, then its compass side among the rest.

Each record keeps the other name: `gloss_name` (the fallback) and `name_from` ("language" or "gloss"). Applying twice is harmless.
No naming logic beyond the fallback lives here: the languages own the words."""
from __future__ import annotations

import json
from pathlib import Path

from .years import years_ago

COMPASS = ("western", "central", "eastern")  # (the last tie-break among cultures that share a name, a founding date and a way of life)


# ------------------------------------------------------------------ gloss names (PW-1249)
def base_gloss(c: dict, people_short: str) -> str:
    """A culture's plain description, as cultures.document has always built it: '<adapted> <first> <people> of <place>'."""
    nm = f"{c['adapted'] + ' ' if c.get('adapted') else ''}{'first ' if c.get('how') == 'founding' else ''}{people_short}"
    return nm + (f" of {c['place']}" if c.get("place") else "")


def _way(c: dict) -> str | None:
    w = next(iter((c.get("traits") or {}).get("ways_now") or {}), None)
    return None if w in (None, c.get("people")) else str(w).replace("_", " ")


def gloss_names(cultures: list[dict], people_short: dict) -> list[str]:
    """Distinct gloss names for cultures.json records (PW-1249), in their order. A name used once stays as it is; a repeat takes
    ', founded <date>' (its born_kyr, three significant figures); one still shared takes its way of life now ('herders'); one still
    shared takes its side of the group by longitude (western, central, eastern) or, past three, its latitude and longitude."""
    base = [base_gloss(c, people_short.get(c["people"], c["people"])) for c in cultures]
    out = list(base)

    def groups(names):
        g: dict = {}
        for i, n in enumerate(names):
            g.setdefault(n, []).append(i)
        return [ix for ix in g.values() if len(ix) > 1]

    for ix in groups(out):
        for i in ix:
            out[i] = f"{base[i]}, founded {years_ago(cultures[i]['born_kyr'], calendar=False)}"
    for ix in groups(out):
        ways = {i: _way(cultures[i]) for i in ix}
        if len(set(ways.values())) > 1:
            for i in ix:
                if ways[i]:
                    out[i] += f", {ways[i]}"
    for ix in groups(out):
        ix = sorted(ix, key=lambda i: (cultures[i].get("lon") or 0.0, i))
        for k, i in enumerate(ix):
            c = cultures[i]
            if len(ix) <= 3 and len({cultures[j].get("lon") for j in ix}) == len(ix):
                tag = (COMPASS[0], COMPASS[2]) if len(ix) == 2 else COMPASS
                out[i] += f", {tag[k]}"
            else:
                out[i] += f", at {c.get('lat') or 0:.1f}, {c.get('lon') or 0:.1f}" if c.get("lat") is not None else f", the {k + 1}th"
    return out


def people_short(lines: list[dict]) -> dict:
    """people id -> its short name ('humans'), as cultures.document writes it."""
    return {l["id"]: (l.get("name") or l["id"]).split(" (")[0] for l in lines}


# ------------------------------------------------------------------ the languages' names
def _lang_names(lang: dict | None) -> dict:
    return ((lang or {}).get("names") or {}) if isinstance(lang, dict) else {}


def place_names(lang: dict | None) -> dict[int, str]:
    """site id -> its name in the languages (the book spelling), for every settlement languages.json names."""
    out = {}
    for d in (_lang_names(lang).get("demes") or {}).values():
        for s in d.get("settlements") or []:
            if s.get("site") is not None and s.get("roman"):
                out[int(s["site"])] = s["roman"]
    return out


def place_english(lang: dict | None) -> dict[int, str]:
    """site id -> the Common's English name for it (PW-1654: `english`, a calque of the name's meaning), where the languages
    give one."""
    out = {}
    for d in (_lang_names(lang).get("demes") or {}).values():
        for s in d.get("settlements") or []:
            if s.get("site") is not None and s.get("english"):
                out[int(s["site"])] = s["english"]
    return out


def culture_lang_names(cultures: list[dict], lang: dict | None, deme_cells: dict | None = None) -> list[str | None]:
    """Each culture's name in the languages (None where it has none): the endonym of its largest living deme (deme_cells: deme id ->
    cells now; without it the culture's last listed deme that has a name). Forms two living cultures would share take their deme's
    river or lake name."""
    D = _lang_names(lang).get("demes") or {}
    if not D:
        return [None] * len(cultures)
    pick = []
    for c in cultures:
        ds = [d for d in c.get("demes") or [] if (D.get(str(d)) or {}).get("name") and (D[str(d)].get("people") in (None, c["people"]))]
        if not ds or c.get("end") is not None:
            pick.append(None)
            continue
        d = max(ds, key=lambda x: ((deme_cells or {}).get(x, 0), x))
        pick.append(str(d))
    out = [D[d]["name"]["roman"] if d else None for d in pick]
    seen: dict = {}
    for i, n in enumerate(out):
        if n:
            seen.setdefault(n, []).append(i)
    for n, ix in seen.items():
        if len(ix) < 2:
            continue
        for i in ix:
            pl = next((p for p in D[pick[i]].get("places") or [] if p.get("kind") in ("river", "lake") and p.get("roman")), None)
            if pl:
                out[i] = f"{n} of {pl['roman']}"
    seen = {}
    for i, n in enumerate(out):  # (still shared: the gloss decides)
        if n:
            seen.setdefault(n, []).append(i)
    for ix in seen.values():
        if len(ix) > 1:
            for i in ix:
                out[i] = None
    return out


# ------------------------------------------------------------------ filling the slot
def _set(rec: dict, name: str | None, gloss: str) -> None:
    rec["gloss_name"] = gloss
    rec["name"] = name or gloss
    rec["name_from"] = "language" if name else "gloss"


def apply_cultures(cdoc: dict, lines: list[dict], lang: dict | None = None, deme_cells: dict | None = None) -> dict:
    """Fills the slot of every culture of a cultures.json doc (in place; returned). The gloss is remade from the record (PW-1249), so a
    cultures.json made before it reads with distinct names too; merge texts are rewritten with the slot names."""
    C = cdoc.get("cultures") or []
    if not C:
        return cdoc
    gl = gloss_names(C, people_short(lines))
    ln = culture_lang_names(C, lang, deme_cells)
    for c, g, n in zip(C, gl, ln):
        _set(c, n, g)
    for m in cdoc.get("merges") or []:
        if "text" in m and m.get("culture") is not None and m.get("into") is not None:
            why = m["text"].rsplit(" (", 1)[-1] if " (" in m["text"] else ""
            m["text"] = f"{C[m['culture']]['name']} merged into {C[m['into']]['name']}" + (f" ({why}" if why else "")
    return cdoc


def apply_faiths(gods_doc: dict, cultures: list[dict]) -> dict:
    """Faith names (gods doc `faiths.list`) composed with the cultures' slot names, as gods.faith_docs composes them; a faith you wrote
    keeps its name. Also the doc's per-culture names and pantheon hub names. In place; returned."""
    if not gods_doc or not cultures:
        return gods_doc
    word = {"founded": "faith", "schism": "schism"}
    for f in ((gods_doc.get("faiths") or {}).get("list") or []):
        if f.get("authored"):
            f.setdefault("gloss_name", f["name"])
            f["name_from"] = "authored"
            continue
        oc = f.get("origin_culture")
        if oc is None or not 0 <= oc < len(cultures):
            continue
        c = cultures[oc]
        g = f"the {f['core']} {word.get(f.get('how'), 'faith')} of {c.get('gloss_name') or c['name']}"
        n = f"the {f['core']} {word.get(f.get('how'), 'faith')} of {c['name']}" if c.get("name_from") == "language" else None
        _set(f, n, g)
    for k, cu in (gods_doc.get("cultures") or {}).items():
        try:
            cu["name"] = cultures[int(k)]["name"]
        except (ValueError, IndexError, KeyError):
            pass
    for p in ((gods_doc.get("pantheons") or {}).get("list") or []):
        h = p.get("hub")
        if h is not None and 0 <= h < len(cultures):
            p["hub_name"] = cultures[h]["name"]
            p["name"] = f"the {cultures[h]['name']} pantheon"
    return gods_doc


def apply_polities(pdoc: dict, lang: dict | None, cultures: list[dict] | None = None) -> dict:
    """State names (polities doc or its summary) from their capital's name in the languages, composed as polities._name composes them;
    unchanged without a languages.json. The doc's culture list takes the slot names. In place; returned."""
    if not pdoc:
        return pdoc
    if cultures:
        for u, x in (pdoc.get("cultures") or {}).items():
            i = x.get("id")
            if i is not None and 0 <= i < len(cultures):
                x["name"] = cultures[i]["name"]
    P = pdoc.get("polities") or []
    places = place_names(lang)
    if not places:
        for rec in P:
            rec.setdefault("gloss_name", rec.get("name"))
            rec["name_from"] = "gloss"
        return pdoc
    count: dict = {}
    plan = []
    for rec in P:
        site = (rec.get("capital") or {}).get("site")
        pl = places.get(int(site)) if site is not None else None
        if rec.get("gloss_names") is None:
            rec["gloss_names"] = [list(x) for x in rec.get("names") or []]
        if pl is None or rec.get("kind") == "dragon":
            plan.append((rec, None))
            continue
        tier = rec.get("tier_peak")
        spans = []
        for a, ppl, short in rec.get("peoples") or []:
            nm = f"{pl} ({short})"
            if tier == "chiefdom":
                nm = "Chiefdom in " + nm
            count[nm] = count.get(nm, 0) + 1
            spans.append([a, nm, count[nm]])
        plan.append((rec, spans))
    for rec, spans in plan:
        gl = rec["gloss_names"]
        g = (_span_at(gl, rec.get("peak_kyr")) if gl else rec.get("gloss_name") or rec.get("name"))
        if not spans:
            rec["names"] = gl or rec.get("names")
            _set(rec, None, g)
            continue
        rec["names"] = [[a, nm + (f" {k}" if k > 1 else "")] for a, nm, k in spans]  # ('Iligya (humans) 2': the second so named)
        _set(rec, _span_at(rec["names"], rec.get("peak_kyr")), g)
    return pdoc


def _span_at(spans: list, ago) -> str:
    out = spans[0]
    for s in spans:
        if ago is None or s[0] >= ago - 1e-9:
            out = s
    return out[1]


def deme_cells(run_dir: Path) -> dict:
    """deme id -> cells now, from the run's demes.json ({} without one)."""
    f = Path(run_dir) / "demes.json"
    if not f.exists():
        return {}
    try:
        return {d["id"]: d.get("cells_now") or 0 for d in json.loads(f.read_text())["demes"]}
    except (ValueError, KeyError):
        return {}


def slot(cdoc: dict | None, gods_doc: dict | None = None, pdoc: dict | None = None, settlements: list | None = None,
         lang: dict | None = None) -> dict:
    """The whole slot as one table for the viewer and the CLI: {"cultures": {id: {name, gloss_name, name_from}}, "faiths": ...,
    "states": ..., "places": {site: {...}}} from docs the slot has already been applied to (places: the settlement ledger's sites)."""
    pick = lambda r: {k: r.get(k) for k in ("name", "gloss_name", "name_from")}  # noqa: E731
    out = {"cultures": {str(c["id"]): pick(c) for c in (cdoc or {}).get("cultures") or []},
           "faiths": {str(f["id"]): pick(f) for f in ((gods_doc or {}).get("faiths") or {}).get("list") or []},
           "states": {str(r["id"]): pick(r) for r in (pdoc or {}).get("polities") or []}, "places": {}}
    pn, en = place_names(lang), place_english(lang)
    for s in settlements or []:
        if s.get("tier_peak") in ("town", "city") or s["id"] in pn:
            n = pn.get(s["id"])
            out["places"][str(s["id"])] = {"name": n or s.get("place"), "gloss_name": s.get("place"),
                                           "name_from": "language" if n else "gloss", "local": n, "english": en.get(s["id"])}
    return out
