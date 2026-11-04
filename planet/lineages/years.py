"""Dates as text for readouts (PW-1429). A leaf module: import it from anywhere in planet/lineages."""


def years_ago(kyr: float) -> str:
    """A date as text, for readouts (PW-1429): '12,400 years ago', 'the present'. Three significant figures from 1,000
    years up, like the viewer's NumFmt.ago (viewer/numfmt.js), which also shows 'year N' once the present's year is set."""
    if kyr <= 0.0005:
        return "the present"
    y = kyr * 1000
    if y >= 1000:
        m = 10 ** (len(str(int(y))) - 3)
        y = round(y / m) * m
    y = int(round(y))
    return f"{y:,} {'year' if y == 1 else 'years'} ago"
