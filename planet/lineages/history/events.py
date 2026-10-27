"""The event log of a history: origins, extinctions, refuges, lingering hybrids (crossings are logged by crossing.Crossings)."""

from __future__ import annotations


class EventsMixin:
    def _event(self, ago: float, kind: str, line, text: str, lat: float | None = None, lon: float | None = None) -> None:
        """Log an event of `line` (a Lineage), `ago` kyr before the present, at a place (lat/lon) or none."""
        self.events.append({"ago_kyr": round(ago, 3), "kind": kind, "line": line.id, "text": text, "lat": lat, "lon": lon})

    def _event_at(self, ago: float, kind: str, line, text: str, cell: int) -> None:
        """Log an event at a grid cell."""
        g = self.grid
        self._event(ago, kind, line, text, round(float(g.lat[cell]), 2), round(float(g.lon[cell]), 2))
