"""Dates as text for readouts (PW-1429). A leaf module: import it from anywhere in planet/lineages.

A read-out may ask for its dates in a culture's own calendar (PW-1435, calendars.py): `in_calendar(cal)` sets it for the code run
inside the `with` (a context variable, so the server's threads do not share it); years_ago then reads "year 212 of the Founding of
Iligya" for a date from the calendar's epoch on and "340 years before the Founding of Iligya" before it. "X years ago" stays the
default."""
from __future__ import annotations

import contextlib
import contextvars
import math

_CAL: contextvars.ContextVar = contextvars.ContextVar("pw_calendar", default=None)  # ({"name", "epoch_kyr"} or None)


def calendar_date(kyr: float, cal: dict) -> str:
    """A date (kyr ago) in a calendar {name, epoch_kyr}: the epoch's year is year 1 (as AUC 1 and AH 1 are the founding's own
    year); a date before it is 'N years before <name>'."""
    d = (float(cal["epoch_kyr"]) - max(kyr, 0.0)) * 1000.0
    if d > -0.5:
        return f"year {int(math.floor(d + 1e-6)) + 1:,} of {cal['name']}"
    n = int(round(-d))
    return f"{n:,} {'year' if n == 1 else 'years'} before {cal['name']}"


@contextlib.contextmanager
def in_calendar(cal: dict | None):
    """Dates read by years_ago inside the block are written in `cal` ({name, epoch_kyr}; None: years ago)."""
    tok = _CAL.set(cal)
    try:
        yield
    finally:
        _CAL.reset(tok)


def years_ago(kyr: float, calendar: bool = True) -> str:
    """A date as text, for readouts (PW-1429): '12,400 years ago', 'the present'. Three significant figures from 1,000
    years up, like the viewer's NumFmt.ago (viewer/numfmt.js), which also shows 'year N' once the present's year is set.
    Inside in_calendar(cal) (and calendar=True): the date in that calendar instead. calendar=False for text that must not
    change with it (a name)."""
    cal = _CAL.get() if calendar else None
    if cal is not None:
        return calendar_date(kyr, cal)
    if kyr <= 0.0005:
        return "the present"
    y = kyr * 1000
    if y >= 1000:
        m = 10 ** (len(str(int(y))) - 3)
        y = round(y / m) * m
    y = int(round(y))
    return f"{y:,} {'year' if y == 1 else 'years'} ago"
