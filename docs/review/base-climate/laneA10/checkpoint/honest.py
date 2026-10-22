"""pytest plugin / import hook: the ice lane's honest zoom rules as TZParams defaults (PW-570 step 4 checkpoint)."""
from planet.timezoom import params as P

HONEST = dict(orbit_resp="seasons", sheet_air="cold", surface_air="fetch", margin="ramp", front="ramp")
_init = P.TZParams.__init__


def _honest_init(self, *a, **kw):
    for k, v in HONEST.items():
        kw.setdefault(k, v)
    _init(self, *a, **kw)


P.TZParams.__init__ = _honest_init
