"""File-based issue tracker for procgen_world. See issue-tracking/README.md.

Usage (from the repo root):
    uv run python issue-tracking/board.py list [--open] [--status S] [--type T] [--parent ID]
                                           [--subsystem X] [--effort E] [--impact I]
    uv run python issue-tracking/board.py next [--subsystem X] [--limit N]
    uv run python issue-tracking/board.py decisions [--brief]
    uv run python issue-tracking/board.py morning [--hours 24]
    uv run python issue-tracking/board.py tree [ID] [--open]
    uv run python issue-tracking/board.py show ID
    uv run python issue-tracking/board.py new --type T --title "..." --subsystem X --effort E --impact I
                                          [--found-by WHO] [--parent ID] [--status S] [--desc "..."]
                                          [--ref R]... [--relates ID]... [--blocked-by ID]...
    uv run python issue-tracking/board.py update ID "message" [--status S]
    uv run python issue-tracking/board.py intake [--list] [FILE...]
    uv run python issue-tracking/board.py intake --reject FILE "reason"
    uv run python issue-tracking/board.py intake --merge-into PW-NNN FILE
    uv run python issue-tracking/board.py check

Standard library only, so it also runs as plain `python3 issue-tracking/board.py`.
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

PREFIX = "PW"
TYPES = ["epic", "story", "task"]  # order = hierarchy rank
STATUSES = ["todo", "in-progress", "blocked", "needs-decision", "done", "wontdo"]
CLOSED = {"done", "wontdo"}
SUBSYSTEMS = ["tectonics", "surface", "climate", "ocean", "hydrology", "coast", "zoom", "timezoom",
              "highlights", "viewer", "store", "infra", "docs"]
EFFORTS = ["xs", "s", "m", "l", "xl"]  # ascending
IMPACTS = ["low", "med", "high"]  # ascending
LINK_FIELDS = ["blocked_by", "relates"]
LIST_FIELDS = LINK_FIELDS + ["refs"]
FIELDS = ["id", "title", "type", "status", "parent", "subsystem", "effort", "impact", "found_by",
          "blocked_by", "relates", "refs", "created", "updated"]  # the complete schema
DRAFT_FIELDS = [f for f in FIELDS if f not in ("id", "created", "updated")]
ID_RE = re.compile(rf"^{PREFIX}-\d{{3,}}$")
UPDATE_RE = re.compile(r"^- \d{4}-\d{2}-\d{2}: \S")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- frontmatter
# A deliberately small YAML subset: one `key: value` per line, where a value is
# empty/null, a plain or quoted string, a YYYY-MM-DD date, or a flow list
# `[a, "b, c", 'd']`. Text after an unquoted ` #` is a comment.

def _strip_comment(s):
    q = None
    for i, c in enumerate(s):
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip()
    return s.strip()


def _scalar(s):
    s = s.strip()
    if s in ("", "null", "~"):
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if DATE_RE.match(s):
        try:
            return dt.date.fromisoformat(s)
        except ValueError:
            return s
    return s


def _split_list(s):
    items, cur, q = [], "", None
    for c in s:
        if q:
            cur += c
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            cur += c
        elif c == ",":
            items.append(cur)
            cur = ""
        else:
            cur += c
    if q:
        raise ValueError(f"unterminated quote in {s!r}")
    if cur.strip() or items:
        items.append(cur)
    out = []
    for it in items:
        if not it.strip():
            raise ValueError(f"empty list item in [{s}]")
        v = _scalar(it)
        out.append(v.isoformat() if isinstance(v, dt.date) else v)
    return out


def parse_frontmatter(text):
    meta = {}
    for n, raw in enumerate(text.splitlines(), 1):
        ln = _strip_comment(raw)
        if not ln:
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$", ln)
        if not m:
            raise ValueError(f"line {n}: expected 'key: value', got {raw!r}")
        key, val = m.group(1), (m.group(2) or "").strip()
        if key in meta:
            raise ValueError(f"line {n}: duplicate key {key!r}")
        if val.startswith("["):
            if not val.endswith("]"):
                raise ValueError(f"line {n}: list must be on one line as [a, b]")
            meta[key] = _split_list(val[1:-1])
        else:
            meta[key] = _scalar(val)
    return meta


def _fmt(v):
    if v is None:
        return "null"
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, list):
        return "[" + ", ".join(_fmt_item(x) for x in v) + "]"
    s = str(v)
    if (s != s.strip() or not s or s in ("null", "~") or s[0] in "[\"'{&*!|>%@`-"
            or ": " in s or " #" in s or DATE_RE.match(s)):
        return '"' + s.replace('"', "'") + '"'
    return s


def _fmt_item(v):
    s = str(v)
    if re.match(r"^[\w./\-+§→()=]+$", s) and s not in ("null", "~"):
        return s
    return '"' + s.replace('"', "'") + '"'


def dump_frontmatter(meta):
    return "".join(f"{k}: {_fmt(meta.get(k))}\n" for k in FIELDS if k in meta)


def split_file(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        raise ValueError("missing or malformed frontmatter (needs --- lines)")
    return m.group(1), m.group(2)


# ---------------------------------------------------------------- loading

class Board:
    def __init__(self, root):
        self.root = Path(root)
        self.tdir = self.root / "tickets"
        self.inbox = self.root / "inbox"

    def load(self, strict=True):
        """Parse every ticket. Unparseable files go in the error list; with
        strict=True (every command but `check`) any such error aborts."""
        tickets, errors = {}, []
        for path in sorted(self.tdir.glob("*.md")):
            try:
                t = read_ticket(path)
            except ValueError as e:
                errors.append(f"{path.name}: {e}")
                continue
            tid = t.get("id")
            if not isinstance(tid, str) or not ID_RE.match(tid):
                errors.append(f"{path.name}: id {tid!r} is not of the form {PREFIX}-NNN")
                continue
            if tid in tickets:
                errors.append(f"{tid}: duplicate id in {tickets[tid]['_path'].name} and {path.name}")
                continue
            tickets[tid] = t
        if strict and errors:
            sys.exit("\n".join(errors) + "\nRun `board.py check` for a full report.")
        return tickets, errors

    def drafts(self):
        return sorted(p for p in self.inbox.glob("*.md") if p.name.lower() != "readme.md")

    def next_num(self, tickets):
        return max((id_num(i) for i in tickets), default=0) + 1


def read_ticket(path):
    fm, body = split_file(path.read_text())
    meta = parse_frontmatter(fm)
    meta["_keys"] = [k for k in meta]
    meta["_path"] = path
    meta["_body"] = body
    meta["_raw"] = {f: meta.get(f) for f in LIST_FIELDS}
    for f in LIST_FIELDS:
        if not isinstance(meta.get(f), list):
            meta[f] = [] if meta.get(f) is None else meta[f]
    return meta


def write_ticket(path, meta, body):
    path.write_text(f"---\n{dump_frontmatter(meta)}---\n\n{body.lstrip()}")


def id_num(tid):
    return int(tid.split("-")[1])


def today():
    return dt.date.today()


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40].rstrip("-")


# ---------------------------------------------------------------- validation

def problems_for(t, tickets, draft=False):
    """Everything wrong with one ticket (or inbox draft), as messages."""
    out = []
    p = out.append
    keys = t["_keys"]
    allowed = DRAFT_FIELDS if draft else FIELDS
    for k in keys:
        if k not in allowed:
            hint = " (drafts get id/created/updated at intake)" if draft and k in FIELDS else ""
            p(f"unknown field {k!r}{hint} (allowed: {', '.join(allowed)})")
    for k in allowed:
        if k not in keys:
            p(f"missing field {k!r}")

    tid = t.get("id")
    if not draft and not t["_path"].name.startswith(f"{tid}-"):
        p(f"filename {t['_path'].name} does not start with {tid}-")
    if not isinstance(t.get("title"), str) or not t["title"].strip():
        p("title must be a non-empty string")
    for field, allowed_vals in (("type", TYPES), ("status", STATUSES), ("subsystem", SUBSYSTEMS),
                                ("effort", EFFORTS), ("impact", IMPACTS)):
        if t.get(field) not in allowed_vals:
            p(f"bad {field} {t.get(field)!r} (allowed: {', '.join(allowed_vals)})")
    if not isinstance(t.get("found_by"), str) or not t["found_by"].strip():
        p("found_by must name the branch, agent or user (non-empty text)")

    if not draft:
        for k in ("created", "updated"):
            if not isinstance(t.get(k), dt.date):
                p(f"{k} must be a YYYY-MM-DD date, got {t.get(k)!r}")
        if isinstance(t.get("created"), dt.date) and isinstance(t.get("updated"), dt.date):
            if t["updated"] < t["created"]:
                p("updated is earlier than created")

    for f in LIST_FIELDS:
        raw = t["_raw"][f]
        if raw is not None and not isinstance(raw, list):
            p(f"{f} must be a list like [a, b], got {raw!r}")
            continue
        for item in raw or []:
            if not isinstance(item, str):
                p(f"{f} entry {item!r} must be a string")
            elif f in LINK_FIELDS:
                if item not in tickets:
                    p(f"{f} {item} does not exist")
                elif item == tid:
                    p(f"{f} refers to itself")

    parent = t.get("parent")
    if parent is not None:
        if parent not in tickets:
            p(f"parent {parent} does not exist")
        elif t.get("type") in TYPES and tickets[parent].get("type") in TYPES:
            if TYPES.index(tickets[parent]["type"]) >= TYPES.index(t["type"]):
                p(f"{t['type']} cannot sit under {tickets[parent]['type']} {parent}")
        seen, cur = {tid}, parent
        while cur in tickets:
            if cur in seen:
                if cur == tid:
                    p("parent chain loops back to itself")
                break
            seen.add(cur)
            cur = tickets[cur].get("parent")

    if t.get("status") == "blocked" and not t["blocked_by"]:
        p("status blocked but blocked_by is empty")

    body = t["_body"]
    if not re.search(r"^## Description\s*$", body, re.M):
        p("body missing '## Description' section")
    upd = re.search(r"^## Updates\s*$(.*)", body, re.M | re.S)
    if not upd:
        if not draft:
            p("body missing '## Updates' section")
    else:
        entries = [ln for ln in upd.group(1).splitlines() if ln.strip()]
        for ln in entries:
            if ln.startswith("## "):
                break
            if ln.startswith("- ") and not UPDATE_RE.match(ln):
                p(f"update entry not in '- YYYY-MM-DD: text' form: {ln[:60]!r}")
        if not draft and not any(UPDATE_RE.match(ln) for ln in entries):
            p("Updates section has no entries")
    return out


# ---------------------------------------------------------------- views

def line(t):
    mark = "x" if t["status"] in CLOSED else " "
    return (f"[{mark}] {t['id']} {t.get('type', ''):<5} {t.get('status', ''):<14} "
            f"{t.get('subsystem', ''):<10} {t.get('effort', ''):<2} {t.get('impact', ''):<4} {t.get('title', '')}")


def by_id(ts):
    return sorted(ts, key=lambda t: id_num(t["id"]))


def children_of(tickets, tid):
    return by_id(t for t in tickets.values() if t.get("parent") == tid)


def description(t):
    m = re.search(r"^## Description\s*$(.*?)(?=^## |\Z)", t["_body"], re.M | re.S)
    return m.group(1).strip() if m else ""


def update_entries(t):
    m = re.search(r"^## Updates\s*$(.*)", t["_body"], re.M | re.S)
    out = []
    for ln in (m.group(1).splitlines() if m else []):
        if ln.startswith("## "):
            break
        if UPDATE_RE.match(ln):
            out.append((dt.date.fromisoformat(ln[2:12]), ln[14:].strip()))
    return out


def cmd_list(b, tickets, args):
    for t in by_id(tickets.values()):
        if args.open and t["status"] in CLOSED:
            continue
        if any(v and t.get(f) != v for f, v in (("status", args.status), ("type", args.type),
                                                ("parent", args.parent), ("subsystem", args.subsystem),
                                                ("effort", args.effort), ("impact", args.impact))):
            continue
        print(line(t))


def rank_next(tickets, subsystem=None):
    """Actionable tickets (todo / in-progress, not epics), cheapest and most
    valuable first: effort ascending, then impact descending, then id."""
    ts = [t for t in tickets.values()
          if t["status"] in ("todo", "in-progress") and t["type"] != "epic"
          and (not subsystem or t.get("subsystem") == subsystem)]
    return sorted(ts, key=lambda t: (EFFORTS.index(t["effort"]) if t.get("effort") in EFFORTS else 99,
                                     -(IMPACTS.index(t["impact"]) if t.get("impact") in IMPACTS else -1),
                                     id_num(t["id"])))


def cmd_next(b, tickets, args):
    ts = rank_next(tickets, args.subsystem)
    for t in ts[:args.limit] if args.limit else ts:
        print(line(t))


def cmd_decisions(b, tickets, args):
    ts = by_id(t for t in tickets.values() if t["status"] == "needs-decision")
    if not ts:
        print("No tickets need a decision.")
    for t in ts:
        print(line(t))
        if not args.brief:
            print("\n" + description(t) + "\n")


def cmd_morning(b, tickets, args):
    now = dt.datetime.now()
    since = (now - dt.timedelta(hours=args.hours)).date()
    print(f"# Board digest, {now:%Y-%m-%d %H:%M}\n")
    dec = by_id(t for t in tickets.values() if t["status"] == "needs-decision")
    print(f"## Decisions needed ({len(dec)})\n")
    for t in dec:
        print(f"### {t['id']}: {t['title']}\n*{t['subsystem']}, effort {t['effort']}, impact {t['impact']}*\n")
        print(description(t) + "\n")
    if not dec:
        print("None.\n")
    recent = [t for t in tickets.values()
              if isinstance(t.get("updated"), dt.date) and t["updated"] >= since and t["status"] != "needs-decision"]
    print(f"## Updated since {since} ({len(recent)})\n")
    for sub in SUBSYSTEMS:
        ts = by_id(t for t in recent if t.get("subsystem") == sub)
        if not ts:
            continue
        print(f"### {sub}\n")
        for t in ts:
            print(f"- **{t['id']}** [{t['status']}] {t['title']} ({t['effort']}/{t['impact']})")
            for d, text in update_entries(t):
                if d >= since:
                    print(f"  - {d}: {text}")
        print()


def cmd_tree(b, tickets, args):
    visited = set()

    def walk(t, depth):
        if (args.open and t["status"] in CLOSED) or t["id"] in visited:
            return
        visited.add(t["id"])
        print("    " * depth + line(t))
        for c in children_of(tickets, t["id"]):
            walk(c, depth + 1)

    if args.id:
        walk(get(tickets, args.id), 0)
        return
    roots = [t for t in tickets.values() if not t.get("parent") or t["parent"] not in tickets]
    for t in by_id(r for r in roots if r["type"] == "epic"):
        walk(t, 0)
    loose = [r for r in roots if r["type"] != "epic" and not (args.open and r["status"] in CLOSED)]
    for sub in SUBSYSTEMS:
        ts = [t for t in loose if t.get("subsystem") == sub]
        if ts:
            print(f"\n({sub}, no parent)")
            for t in by_id(ts):
                walk(t, 0)


def cmd_show(b, tickets, args):
    t = get(tickets, args.id)
    print(t["_path"].read_text().rstrip())
    blocks = [o["id"] for o in by_id(tickets.values()) if t["id"] in o["blocked_by"]]
    related_by = [o["id"] for o in by_id(tickets.values()) if t["id"] in o["relates"]]
    print("\n--- computed ---")
    print(f"blocks:     {', '.join(blocks) or '-'}")
    print(f"related by: {', '.join(related_by) or '-'}")
    kids = children_of(tickets, t["id"])
    print("children:" + ("" if kids else "   -"))
    for c in kids:
        print("    " + line(c))


# ---------------------------------------------------------------- editing

def new_body(desc, first_update):
    return f"## Description\n{(desc or '').strip()}\n\n## Updates\n- {today()}: {first_update}\n"


def create(b, tickets, meta, body):
    """Give `meta` the next id, validate it against the board, write it.
    Returns (path, problems); nothing is written if there are problems."""
    tid = f"{PREFIX}-{b.next_num(tickets):03d}"
    full = {"id": tid, **{k: meta.get(k) for k in DRAFT_FIELDS}, "created": today(), "updated": today()}
    for f in LIST_FIELDS:
        full[f] = list(full.get(f) or [])
    path = b.tdir / f"{tid}-{slugify(full['title'] or 'untitled')}.md"
    t = dict(full, _keys=list(FIELDS), _path=path, _body=body, _raw={f: full[f] for f in LIST_FIELDS})
    probs = problems_for(t, {**tickets, tid: t})
    if probs:
        return None, probs
    b.tdir.mkdir(parents=True, exist_ok=True)
    write_ticket(path, full, body)
    tickets[tid] = t
    return path, []


def cmd_new(b, tickets, args):
    if args.parent:
        args.parent = get(tickets, args.parent)["id"]
    meta = {"title": args.title, "type": args.type, "status": args.status, "parent": args.parent,
            "subsystem": args.subsystem, "effort": args.effort, "impact": args.impact,
            "found_by": args.found_by, "blocked_by": args.blocked_by, "relates": args.relates, "refs": args.ref}
    path, probs = create(b, tickets, meta, new_body(args.desc, "Created."))
    if probs:
        sys.exit("Not created:\n  " + "\n  ".join(probs))
    print(path.relative_to(b.root.parent))


def add_update(t, msg, status=None):
    path = t["_path"]
    text = path.read_text()
    if status and status != t["status"]:
        text = re.sub(r"^status:.*$", f"status: {status}", text, count=1, flags=re.M)
        msg = f"Status {t['status']} -> {status}. {msg}".strip()
    text = re.sub(r"^updated:.*$", f"updated: {today()}", text, count=1, flags=re.M)
    if not re.search(r"^## Updates\s*$", text, re.M):
        text = text.rstrip() + "\n\n## Updates\n"
    text = re.sub(r"^## Updates[ \t]*\n(\s*\n)*", lambda m: f"## Updates\n- {today()}: {msg}\n", text,
                  count=1, flags=re.M)
    path.write_text(text)
    return msg


def cmd_update(b, tickets, args):
    t = get(tickets, args.id)
    print(f"{t['id']}: {add_update(t, args.message, args.status)}")


def read_draft(path):
    t = read_ticket(path)
    t.setdefault("id", None)
    return t


def cmd_intake(b, tickets, args):
    if args.reject:
        path = draft_path(b, args.reject[0])
        path.unlink()
        print(f"Rejected {path.name}: {args.reject[1]}")
        return
    if args.merge_into:
        tid, fname = args.merge_into
        t = get(tickets, tid)
        path = draft_path(b, fname)
        try:
            d = read_draft(path)
        except ValueError as e:
            sys.exit(f"{path.name}: {e}")
        desc = description(d)
        text = (f"Merged inbox draft {path.name} (\"{d.get('title')}\", found by {d.get('found_by') or '?'})."
                + ("\n  " + desc.replace("\n", "\n  ") if desc else ""))
        new_refs = [r for r in d.get("refs") or [] if r not in t["refs"]]
        add_update(t, text)
        if new_refs:
            t2 = read_ticket(t["_path"])
            meta = {k: t2.get(k) for k in FIELDS}
            meta["refs"] = t2["refs"] + new_refs
            write_ticket(t["_path"], meta, t2["_body"])
        path.unlink()
        print(f"Merged {path.name} into {t['id']}" + (f" (+refs {', '.join(new_refs)})" if new_refs else ""))
        return

    paths = [draft_path(b, f) for f in args.files] if args.files else b.drafts()
    if not paths:
        print("Inbox is empty.")
        return
    failed = 0
    for path in paths:
        try:
            d = read_draft(path)
        except ValueError as e:
            print(f"  {path.name}: {e}")
            failed += 1
            continue
        head = (f"{path.name}: [{d.get('type')}/{d.get('subsystem')}/{d.get('effort')}/{d.get('impact')}] "
                f"{d.get('title')} (found by {d.get('found_by')})")
        probs = problems_for(d, tickets, draft=True)
        if args.list:
            print(head + ("".join(f"\n    ! {x}" for x in probs)))
            continue
        if probs:
            print(f"SKIPPED {head}" + "".join(f"\n    ! {x}" for x in probs))
            failed += 1
            continue
        body = d["_body"]
        note = f"Created from inbox draft {path.name} (found by {d['found_by']})."
        if re.search(r"^## Updates\s*$", body, re.M):
            body = re.sub(r"^## Updates[ \t]*\n(\s*\n)*", lambda m: f"## Updates\n- {today()}: {note}\n",
                          body, count=1, flags=re.M)
        else:
            body = body.rstrip() + f"\n\n## Updates\n- {today()}: {note}\n"
        new, probs = create(b, tickets, d, body)
        if probs:
            print(f"SKIPPED {head}" + "".join(f"\n    ! {x}" for x in probs))
            failed += 1
            continue
        path.unlink()
        print(f"{new.stem[:len(PREFIX) + 4]} <- {head}")
    if failed:
        sys.exit(f"{failed} draft(s) left in the inbox; fix them, --reject or --merge-into.")


def draft_path(b, name):
    p = Path(name)
    if not p.is_absolute():
        p = b.inbox / p.name
    if not p.exists():
        sys.exit(f"No draft {p}")
    return p


def cmd_check(b, tickets, args):
    problems = list(args.load_errors)
    for tid, t in tickets.items():
        problems += [f"{tid}: {m}" for m in problems_for(t, tickets)]
    n_drafts = 0
    for path in b.drafts():
        n_drafts += 1
        try:
            d = read_draft(path)
        except ValueError as e:
            problems.append(f"inbox/{path.name}: {e}")
            continue
        problems += [f"inbox/{path.name}: {m}" for m in problems_for(d, tickets, draft=True)]
    print("\n".join(problems) if problems else f"OK ({len(tickets)} tickets, {n_drafts} inbox drafts)")
    sys.exit(1 if problems else 0)


def get(tickets, tid):
    tid = tid.upper()
    if re.match(r"^\d+$", tid):
        tid = f"{PREFIX}-{int(tid):03d}"
    if tid not in tickets:
        sys.exit(f"No ticket {tid}")
    return tickets[tid]


# ---------------------------------------------------------------- CLI

def main(argv=None):
    p = argparse.ArgumentParser(description="procgen_world issue tracker")
    p.add_argument("--root", default=str(Path(__file__).parent), help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="flat filtered list")
    s.add_argument("--open", action="store_true", help="hide done/wontdo")
    s.add_argument("--status", choices=STATUSES)
    s.add_argument("--type", choices=TYPES)
    s.add_argument("--parent")
    s.add_argument("--subsystem", choices=SUBSYSTEMS)
    s.add_argument("--effort", choices=EFFORTS)
    s.add_argument("--impact", choices=IMPACTS)

    s = sub.add_parser("next", help="actionable tickets, effort ascending then impact descending")
    s.add_argument("--subsystem", choices=SUBSYSTEMS)
    s.add_argument("--limit", type=int)

    s = sub.add_parser("decisions", help="needs-decision tickets with their descriptions")
    s.add_argument("--brief", action="store_true", help="one line each")

    s = sub.add_parser("morning", help="markdown digest: decisions + recently updated, by subsystem")
    s.add_argument("--hours", type=float, default=24)

    s = sub.add_parser("tree", help="hierarchy view")
    s.add_argument("id", nargs="?")
    s.add_argument("--open", action="store_true", help="hide done/wontdo")

    s = sub.add_parser("show", help="one ticket plus computed links and children")
    s.add_argument("id")

    s = sub.add_parser("new", help="create a ticket with the next id (coordinator, on main)")
    s.add_argument("--type", choices=TYPES, required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--subsystem", choices=SUBSYSTEMS, required=True)
    s.add_argument("--effort", choices=EFFORTS, required=True)
    s.add_argument("--impact", choices=IMPACTS, required=True)
    s.add_argument("--found-by", default="coordinator")
    s.add_argument("--parent")
    s.add_argument("--status", choices=STATUSES, default="todo")
    s.add_argument("--desc")
    s.add_argument("--ref", action="append", default=[])
    s.add_argument("--relates", action="append", default=[])
    s.add_argument("--blocked-by", action="append", default=[])

    s = sub.add_parser("update", help="add a dated update entry, optionally change status")
    s.add_argument("id")
    s.add_argument("message", nargs="?", default="")
    s.add_argument("--status", choices=STATUSES)

    s = sub.add_parser("intake", help="number inbox drafts into tickets (coordinator, after merging)")
    s.add_argument("files", nargs="*", help="only these drafts (default: all)")
    s.add_argument("--list", action="store_true", help="list drafts and their problems, change nothing")
    s.add_argument("--reject", nargs=2, metavar=("FILE", "REASON"), help="delete a draft")
    s.add_argument("--merge-into", nargs=2, metavar=("ID", "FILE"),
                   help="append a draft to an existing ticket as an update, then delete it")

    sub.add_parser("check", help="validate all tickets and inbox drafts")

    args = p.parse_args(argv)
    b = Board(args.root)
    tickets, args.load_errors = b.load(strict=args.cmd != "check")
    {"list": cmd_list, "next": cmd_next, "decisions": cmd_decisions, "morning": cmd_morning,
     "tree": cmd_tree, "show": cmd_show, "new": cmd_new, "update": cmd_update,
     "intake": cmd_intake, "check": cmd_check}[args.cmd](b, tickets, args)


if __name__ == "__main__":
    main()
