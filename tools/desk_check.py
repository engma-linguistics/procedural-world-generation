"""Owner's Desk staleness check (.claude/skills/owner-desk/SKILL.md): run before every publish; exit 1 lists what to prune.

Flags:
- a decision card (id line names D<n> and PW- tickets) whose tickets are no longer needs-decision: he has ruled, so the card goes;
- a viewer link to a run, world or zoom that no longer exists on disk;
- a kicker date that isn't today;
- a settled list longer than SETTLED_MAX items (settled items belong in docs/wiki/decisions.md once he has seen them);
- a running-row lane that a merge commit on main already names (finished lanes come off the table).

    uv run python tools/desk_check.py [desk.html]
"""

import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESK = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/review/owner-desk/index.html"
TICKETS = ROOT / "issue-tracking/tickets"
SETTLED_MAX = 20


def ticket_status(tid):
    for f in TICKETS.glob(f"{tid}-*.md"):
        m = re.search(r"^status:\s*(\S+)", f.read_text(), re.M)
        return m.group(1) if m else None
    return None


def main():
    s = DESK.read_text()
    problems = []

    for m in re.finditer(r'<div class="card" id="([^"]+)"><div class="id">(.*?)</div>', s, re.S):
        cid, line = m.group(1), m.group(2)
        if not re.match(r"D\d+", line.strip()):
            continue
        ids = re.findall(r"PW-\d+", line)
        settled = [t for t in ids if ticket_status(t) != "needs-decision"]
        if ids and len(settled) == len(ids):
            problems.append(f"card {cid}: {', '.join(f'{t} is {ticket_status(t)}' for t in ids)}; ruled, so remove the card")

    for kind, rx, where in (("run", r"[?&]run=([0-9a-f]{6})", "runs/{}"), ("world", r"[?&]world=([0-9a-f]{6})", "worlds/{}.json"),
                            ("zoom", r"[?&]zoom=([0-9a-f]{6})", "zooms/{}")):
        for i in sorted(set(re.findall(rx, s))):
            if not (ROOT / where.format(i)).exists():
                problems.append(f"link to {kind} {i}, which no longer exists")

    k = re.search(r'<div class="kicker">[^<]*?(\w+day) (\d+) (\w+) (\d{4})', s)
    today = datetime.date.today()
    if not k or datetime.datetime.strptime(" ".join(k.groups()[1:]), "%d %B %Y").date() != today:
        problems.append(f"kicker date is not today ({today:%A %-d %B %Y})")

    if '<h2 id="settled">' in s:
        part = s[s.index('<h2 id="settled">'):]
        part = part[:re.search(r"<h2 |<footer", part[1:]).start() + 1] if re.search(r"<h2 |<footer", part[1:]) else part
        depth, n = 0, 0
        for tag in re.findall(r"</?ul>|<li>", part):  # (top-level items across every list in the section)
            depth += {"<ul>": 1, "</ul>": -1}.get(tag, 0)
            n += tag == "<li>" and depth == 1
        if n > SETTLED_MAX:
            problems.append(f"settled list has {n} items (max {SETTLED_MAX}): move what he has seen to docs/wiki/decisions.md")

    running = s[s.index('<h2 id="coming">'):] if '<h2 id="coming">' in s else ""
    running = running[:running.index("</table>")] if "</table>" in running else ""
    for lane in re.findall(r"<tr><td>(\d{3}) ·", running):
        log = subprocess.run(["git", "-C", str(ROOT), "log", "main", "--merges", "--oneline", "-200", f"--grep=lane {lane}\\b"],
                             capture_output=True, text=True).stdout
        if log.strip():
            problems.append(f"running row {lane}: lane {lane} is merged into main ({log.split(chr(10))[0][:60]}); move it to settled")

    for p in problems:
        print("STALE:", p)
    print("desk_check:", "OK" if not problems else f"{len(problems)} to prune")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
