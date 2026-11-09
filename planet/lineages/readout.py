"""The read-out context (PW-1582): brief.Ctx plus the two docs the server derives for its tabs.

brief.Ctx opens a run and its world and imports nothing from the server, so the code the peoples' caches hash (planet/provenance.py,
the "lineages" scope: trade.derive and the gods that read its goods ledger, PW-1523) stays clear of server.py and api.py. The briefs
(brief.build, the culinary sheets) also want the Religion tab's gods and taboos docs and the Trade tab's exchange doc, which only the
server derives (with the .godscache disk cache); this subclass reads those, and only the read-out layer (the server, the CLI) imports it.
"""
from __future__ import annotations

from pathlib import Path

from . import brief as BR


class Ctx(BR.Ctx):
    def __init__(self, run_ref):
        super().__init__(run_ref)
        self._religion = False  # (gods.json and taboos.json, if the run has them: religion())
        self._trade_flows = False  # (the exchange doc, server.trade_flow_doc, on first use: trade_flows())

    def religion(self) -> tuple[dict | None, dict | None]:
        """(gods doc, taboos doc) of the run as the Religion tab shows them: its authored faiths and saved gods mode included (server.gods_doc /
        taboos_doc, with the .godscache disk cache; PW-1440). Each None where the run has no cultures to derive from."""
        if self._religion is False:
            from .. import server
            try:
                gd = server.gods_doc(self.dir)
                tb = server.taboos_doc(self.dir)
            except (SystemExit, FileNotFoundError, KeyError):
                gd = tb = None
            cu = self.cultures() if gd is not None and hasattr(self, "cultures") else None
            if cu:  # (faith names in the names slot, PW-1436)
                from . import nameslot as NS
                NS.apply_faiths(gd, cu["cultures"])
            self._religion = (gd, tb)
        return self._religion

    def trade_flows(self) -> dict | None:
        """The run's exchange doc (trade_flow.py, PW-1503) as the Trade tab shows it (server.trade_flow_doc, with the .godscache disk cache:
        a minute or two at L7 the first time for a run), None on a run without a land-use window or a world. A harness may set it first."""
        if self._trade_flows is False:
            self._trade_flows = None
            if self.meta.get("eraq") and self.world_id and self.meta.get("kind") == "peoples":
                from .. import server
                try:
                    self._trade_flows = server.trade_flow_doc(self.dir)
                except (SystemExit, FileNotFoundError, KeyError):
                    self._trade_flows = None
        return self._trade_flows


def build(run_ref, region: tuple | None = None, people: str | None = None, era_kyr: float = 0.0, ctx: Ctx | None = None,
          culture: int | None = None) -> dict:
    """brief.build on a read-out context."""
    return BR.build(run_ref, region=region, people=people, era_kyr=era_kyr, ctx=ctx or Ctx(run_ref), culture=culture)


def all_briefs(run_ref, out_dir, eras=BR.DEFAULT_ERAS, log=print) -> list[Path]:
    """brief.all_briefs on a read-out context."""
    return BR.all_briefs(Ctx(run_ref), out_dir, eras=eras, log=log)
