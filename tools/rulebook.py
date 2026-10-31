#!/usr/bin/env python3
"""Search the owner's local D&D 5e rulebooks (PHB, DMG) and cite printed pages.

The PDFs live in docs/references/dnd/ and are gitignored, as is the per-page
text cache (docs/references/dnd/.cache/).  NEVER commit either.

  uv run python tools/rulebook.py index [--force]
  uv run python tools/rulebook.py search <regex> [--book phb|dmg] [--context N] [--pages A-B]
  uv run python tools/rulebook.py page <book> <printed page> [--split] [--pdf]
  uv run python tools/rulebook.py offsets        # re-detect printed-vs-PDF offsets

The text layer is OCR, so expect odd spacing ("Flu mph", "Aying" for "flying");
use loose regexes (e.g. "gold\\s*dragon", "dra\\s*gon").
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DND = ROOT / "docs" / "references" / "dnd"
CACHE = DND / ".cache"
PDFTOTEXT = "pdftotext"

BOOKS = {"phb": DND / "phb-5e.pdf", "dmg": DND / "dmg-5e.pdf"}
NAMES = {"phb": "PHB", "dmg": "DMG"}

# printed page = pdf page + offset.
# DMG: offset 0 for every page (verified from ~90 printed footers, pdf 4..320).
# PHB: the scan has NO page numbers in its text layer and ~27 pages were dropped,
# so the offset creeps up from 1 to 23.  PHB_RUNS lists [first_pdf, last_pdf, offset]
# for stretches anchored by TOC entries, the index and spell headings of known
# page (see docs/references/dnd/README.md).  A pdf page BETWEEN two runs is
# uncertain: it is reported as a range of printed pages ("p.232-233?").
PHB_RUNS = [
    [4, 7, 1], [8, 12, 3], [13, 20, 4], [22, 38, 5], [40, 113, 6], [114, 118, 7],
    [123, 123, 8], [135, 146, 9], [149, 149, 10], [152, 153, 11], [160, 165, 13],
    [167, 169, 14], [170, 170, 15], [173, 182, 16], [183, 183, 18], [192, 212, 19],
    [214, 226, 20], [229, 246, 21], [248, 263, 22], [264, 270, 23],
]
PHB_TAIL = (23, 25)  # pdf 271..293 (appendices B-E, index): between 23 and 25


def offset_range(book: str, pdf: int) -> tuple[int, int]:
    """(lowest, highest) plausible offset for this pdf page; equal when certain."""
    if book == "dmg":
        return (0, 0)
    runs = PHB_RUNS
    if pdf < runs[0][0]:
        return (1, 1)
    for i, (lo, hi, off) in enumerate(runs):
        if lo <= pdf <= hi:
            return (off, off)
        if i + 1 < len(runs) and hi < pdf < runs[i + 1][0]:
            return (off, runs[i + 1][2])
    return PHB_TAIL


def pdf_pages(book: str) -> int:
    out = subprocess.run(["pdfinfo", str(BOOKS[book])], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"^Pages:\s+(\d+)", out, re.M).group(1))


def printed_label(book: str, pdf: int) -> str:
    lo, hi = offset_range(book, pdf)
    return f"{pdf + lo}" if lo == hi else f"{pdf + lo}-{pdf + hi}?"


def cache_path(book: str, pdf: int) -> Path:
    return CACHE / book / f"p{pdf:04d}.txt"


def _extract(book: str, pdf: int) -> None:
    txt = subprocess.run(
        [PDFTOTEXT, "-layout", "-f", str(pdf), "-l", str(pdf), str(BOOKS[book]), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    p = cache_path(book, pdf)
    p.write_text(txt.replace("\f", ""))


def cmd_index(args) -> None:
    for book in BOOKS:
        if not BOOKS[book].exists():
            print(f"{book}: {BOOKS[book]} missing, skipped", file=sys.stderr)
            continue
        (CACHE / book).mkdir(parents=True, exist_ok=True)
        n = pdf_pages(book)
        todo = [p for p in range(1, n + 1) if args.force or not cache_path(book, p).exists()]
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(lambda p: _extract(book, p), todo))
        print(f"{book}: {n} pages, {len(todo)} extracted -> {CACHE / book}")


def load(book: str) -> dict[int, str]:
    d = CACHE / book
    if not d.exists():
        sys.exit(f"no cache for {book}; run: uv run python tools/rulebook.py index")
    return {int(p.stem[1:]): p.read_text() for p in sorted(d.glob("p*.txt"))}


NUM = re.compile(r"(?<![\d,.])(\d{1,3})(?![\d,.])")


def footer_number(text: str) -> int | None:
    """Printed page number found in the first/last non-empty lines, if any."""
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    for l in (lines[-1], lines[0], lines[-2] if len(lines) > 1 else ""):
        s = l.strip()
        if re.fullmatch(r"\d{1,3}", s):
            return int(s)
        m = re.match(r"^(\d{1,3})\s{2,}\S", s) or re.search(r"\S\s{2,}(\d{1,3})$", s) \
            or re.search(r"(?:^|\s)(\d{1,3})\s*$", s if s.isupper() or "I" in s else "")
        if m:
            return int(m.group(1))
    return None


def cmd_offsets(args) -> None:
    from collections import Counter
    for book in BOOKS:
        pages = load(book)
        c: Counter[int] = Counter()
        runs = []
        for pdf, t in pages.items():
            n = footer_number(t)
            if n is not None:
                c[n - pdf] += 1
                runs.append((pdf, n - pdf))
        print(f"{book}: offset (printed - pdf) histogram: {c.most_common(6)}  of {len(pages)} pages")
        # report where the dominant offset changes
        dom = c.most_common(1)[0][0]
        off = [(p, o) for p, o in runs if o != dom]
        print(f"  non-dominant footer reads (pdf page, offset): {off[:30]}")


def split_columns(text: str) -> str:
    """Crude two-column split at the emptiest character column near the middle."""
    lines = text.splitlines()
    w = max((len(l) for l in lines), default=0)
    body = [l.ljust(w) for l in lines if l.strip()]
    if len(body) < 8:
        return text
    xs = range(int(w * 0.35), int(w * 0.65))
    ink = {x: sum(1 for l in body if l[x] != " ") for x in xs}
    low = min(ink.values())
    cands = [x for x in xs if ink[x] <= low]
    mid = cands[len(cands) // 2]
    left = "\n".join(l.ljust(w)[:mid].rstrip() for l in lines)
    right = "\n".join(l.ljust(w)[mid:].strip() for l in lines)
    return left + "\n\n" + right


def cmd_search(args) -> None:
    rx = re.compile(args.regex, re.I)
    books = [args.book] if args.book else list(BOOKS)
    lo, hi = (None, None)
    if args.pages:
        a, _, b = args.pages.partition("-")
        lo, hi = int(a), int(b or a)
    hits = 0
    for book in books:
        for pdf, text in load(book).items():
            plo, phi = (pdf + o for o in offset_range(book, pdf))
            if lo is not None and not (plo <= hi and phi >= lo):
                continue
            lines = text.splitlines()
            shown = set()
            for i, l in enumerate(lines):
                if not rx.search(l):
                    continue
                hits += 1
                for j in range(max(0, i - args.context), min(len(lines), i + args.context + 1)):
                    if j in shown:
                        continue
                    shown.add(j)
                    tag = f"{NAMES[book]} p.{printed_label(book, pdf)} (pdf page {pdf})"
                    print(f"{tag}: {lines[j].rstrip()}")
                if args.context:
                    print("--")
    print(f"[{hits} matching lines]", file=sys.stderr)


def cmd_page(args) -> None:
    book = args.book.lower()
    n = pdf_pages(book)
    if args.pdf:
        pdfs = [args.number]
    else:
        pdfs = [q for q in range(1, n + 1)
                if q + offset_range(book, q)[0] <= args.number <= q + offset_range(book, q)[1]]
    if not pdfs:
        sys.exit(f"{book}: printed page {args.number} not in the PDF")
    for pdf in pdfs:
        show_page(book, pdf, args)


def show_page(book, pdf, args):
    p = cache_path(book, pdf)
    if not p.exists():
        sys.exit(f"{book} pdf page {pdf} not in cache; run index")
    text = p.read_text()
    print(f"=== {NAMES[book]} p.{printed_label(book, pdf)} (pdf page {pdf}) ===")
    print(split_columns(text) if args.split else text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("index"); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_index)
    s = sub.add_parser("search"); s.add_argument("regex"); s.add_argument("--book", choices=list(BOOKS))
    s.add_argument("--context", type=int, default=0); s.add_argument("--pages", help="printed range, e.g. 302-305")
    s.set_defaults(f=cmd_search)
    s = sub.add_parser("page"); s.add_argument("book", choices=list(BOOKS)); s.add_argument("number", type=int, help="printed page (default) or PDF page with --pdf")
    s.add_argument("--pdf", action="store_true", help="treat the number as a PDF page")
    s.add_argument("--split", action="store_true", help="print two-column pages as left then right column")
    s.set_defaults(f=cmd_page)
    s = sub.add_parser("offsets"); s.set_defaults(f=cmd_offsets)
    args = ap.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
