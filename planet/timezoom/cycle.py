"""The ice-age cycle's state (PW-440): between ice ages, building, ending.

A glacial cycle on Earth is slow to build (~80-90 kyr) and fast to end (~10 kyr), and its endings
come at summer-sunshine peaks of the ice's latitude, but not at every one: only once the ice is big
and the glacial old (Paillard 1998's three states; Huybers 2011: the insolation an ending needs falls
with the time since the last one). The time zoom's ice-albedo and CO2 feedbacks alone go to a warm or
a cold branch and stay there (PW-030), so the state the ice is in decides how it answers the sun:

  between   the ice is near its interglacial level: everything as without the cycle (all boosts 1x).
  building  entered when the summer sun at the cycling ice's latitude falls below the build_q
            percentile of its own series while there is some extra ice; nothing changes but the clock:
            the glacial's age counts from here, and small sunshine peaks don't interrupt it.
  ending    entered from building when the extra ice is at least end_min (of the planet's sheet
            scale) AND the summer sun beats a bar that falls with the glacial's age, from its series'
            bar_hi percentile at the start to bar_lo at glacial_kyr (the orbit picks the timing;
            nothing forces a length). Inside an ending, ramping in over cycle_tau:
              - the extra ice melts more per degree-day: up to melt_max x, smoothly with the extra ice
                (tanh over the sheet scale; big sheets' margins stand low on their pressed-down beds,
                in warm air);
              - CO2 is released (up to release x co2_cool, about 90 ppm-equivalent) on top of what
                the ice volume sets, at most the extra ice's own drawdown measured from the
                interglacial level and not clipped (the headroom the cold branch's clipped CO2 lacked);
              - marine fronts of the extra ice calve up to calve_max x faster (marine ice-sheet
                instability on beds below the sea).
            It runs until the extra ice is below end_e of the sheet scale (hysteresis), then between;
            or, if the melt-back stops short (no new low by a few m for a precession period: what is
            left can't melt in this climate, e.g. a polar sheet), the next glacial builds from there.
  backstop  a glacial older than backstop x glacial_kyr ends at the next sunshine peak; counted, since
            if it fires often the real knobs are wrong.

Everything is relative to the planet: the sun's percentiles are of its own summer-insolation series
(over max(kyr, 800) kyr) at the latitude where the extra ice first grows; the extra ice is the sea
level below the interglacial level (the highest sea level seen outside an ice age); the sheet scale is
the sea-level equivalent of sheet_h of ice over sheet_share of the planet's land. The boosts act only
beyond the interglacial ice's footprint (the grounded ice at that highest sea level, the start's at
first): an interglacial's own ice (Earth: Antarctica, Greenland) answers as before.
"""

from __future__ import annotations

import math

import numpy as np

from ..orbit import insolation, orbit_at

BETWEEN, BUILDING, ENDING = 0, 1, 2
NAMES = ("between", "building", "ending")


def summer_sun(lat: float, orb) -> float:
    """Mean daily insolation (W/m2) of lat's two midsummer months (as events.cycling_ice_sun)."""
    months = [9, 10] if lat < 0 else [3, 4]
    return float(insolation(*orb, lat=np.array([lat]))[0, months].mean())


def cycling_latitude(lat: np.ndarray, area: np.ndarray, new: np.ndarray) -> float:
    """Where the ice age's extra ice grows: the cells iced now that weren't at the start (new), in the
    hemisphere with more of their area, their area-weighted mean latitude (65 N if there are none)."""
    if not new.any():
        return 65.0
    south = float(area[new & (lat < 0)].sum()) > float(area[new & (lat >= 0)].sum())
    sel = new & ((lat < 0) if south else (lat >= 0))
    return float((lat[sel] * area[sel]).sum() / area[sel].sum())


class Cycle:
    """The cycle's state over a time zoom. step() each step before the forcing; then .r (0..1, the
    ending's ramp), melt_up / calve_up (the boosts on the extra ice) and release (C of CO2 warming
    allowed on top of the ice volume's) are the step's. scale_m: the sheet scale (m of sea level)."""

    def __init__(self, p, step: float, kyr: float, tilt: float, ph, scale_m: float):
        self.p, self.step_kyr, self.kyr, self.tilt, self.ph = p, step, kyr, tilt, ph
        self.on = p.cycle == "on" and scale_m > 0
        self.scale = scale_m
        self.mode, self.t_mode, self.age = BETWEEN, 0.0, 0.0
        self.r = 0.0
        self.sl_ig = 0.0  # m: the interglacial level (the highest sea level seen outside an ice age)
        self.new_high = True  # this step set it (the sim then keeps the interglacial ice's footprint)
        self.q = None
        self.lat = None
        self.modes: list[int] = []
        self.endings: list[dict] = []
        self.builds: list[dict] = []
        self.backstops = 0

    def needs_setup(self, sl: float) -> bool:
        """The cycling latitude is set once the extra ice first passes end_e of the sheet scale."""
        return self.on and self.q is None and self.extra(sl) > self.p.end_e * self.scale

    def setup(self, lat: float) -> None:
        """The summer sun of the cycling latitude over the zoom (and its percentiles, over at least 800 kyr)."""
        self.lat = lat
        n = int(round(max(self.kyr, 800.0) / self.step_kyr)) + 2
        self.q = np.array([summer_sun(lat, orbit_at(i * self.step_kyr, self.p, self.tilt, self.ph))
                           for i in range(n)])
        pc = lambda x: float(np.percentile(self.q, 100 * x))
        self.q_build, self.q_hi, self.q_lo, self.q_mid = (pc(self.p.build_q), pc(self.p.bar_hi), pc(self.p.bar_lo),
                                                          pc(0.5))

    def extra(self, sl: float) -> float:
        return self.sl_ig - sl

    def bar(self) -> float:
        """The sunshine an ending needs at the glacial's age (Huybers 2011: falling linearly)."""
        f = min(self.age / self.p.glacial_kyr, 1.0)
        return self.q_hi - (self.q_hi - self.q_lo) * f

    def _enter(self, mode: int, t: float, sl: float, **info) -> None:
        if mode == ENDING:
            self.e_low, self.t_low = self.extra(sl), t
            self.endings.append({"t": round(t, 1), "age_kyr": round(self.age, 1),
                                 "extra_m": round(self.extra(sl), 1), **info})
        elif mode == BUILDING:
            self.builds.append({"t": round(t, 1)})
        elif mode == BETWEEN and self.mode == ENDING:
            self.endings[-1]["kyr"] = round(self.t_mode, 1)
        self.mode, self.t_mode = mode, 0.0
        if mode == BUILDING:
            self.age = 0.0

    def step(self, s_no: int, sl: float) -> None:
        self.new_high = self.mode == BETWEEN and sl >= self.sl_ig
        if self.new_high:
            self.sl_ig = sl
        if not self.on or self.q is None:
            self.modes.append(self.mode)
            return
        p, t = self.p, s_no * self.step_kyr
        q = self.q[s_no]
        e = self.extra(sl)
        if self.mode == BETWEEN:
            if q < self.q_build and e > p.end_e * self.scale:
                self._enter(BUILDING, t, sl)
        elif self.mode == BUILDING:
            self.age += self.step_kyr
            peak = self.q[s_no] >= self.q[max(s_no - 1, 0)] and self.q[s_no] > self.q[s_no + 1]
            if e <= 0.0:
                self._enter(BETWEEN, t, sl)  # (the ice went back on its own)
            elif e >= p.end_min * self.scale and q >= self.bar():
                self._enter(ENDING, t, sl, sun=round(float(q), 1), bar=round(float(self.bar()), 1), backstop=False)
            elif self.age > p.backstop * p.glacial_kyr and peak and q > self.q_mid:
                self.backstops += 1
                self._enter(ENDING, t, sl, sun=round(float(q), 1), bar=round(float(self.bar()), 1), backstop=True)
        elif self.mode == ENDING:
            if e < self.e_low - 0.25 * p.end_e * self.scale:  # (a new low, by a few m)
                self.e_low, self.t_low = e, t
            if e < p.end_e * self.scale:
                self._enter(BETWEEN, t, sl)
            elif t - self.t_low > p.precession_period:
                # the melt-back has stopped short (a precession cycle without a new low): what is left
                # can't melt in this climate (e.g. a polar sheet); the next glacial builds from here
                self.endings[-1]["stalled_m"] = round(self.e_low, 1)
                self.endings[-1]["kyr"] = round(self.t_mode, 1)
                self._enter(BUILDING, t, sl)
        self.t_mode += self.step_kyr
        # the ending's ramp (and none outside one: between ice ages all is as without the cycle)
        if self.mode == ENDING:
            self.r += (1.0 - math.exp(-self.step_kyr / p.cycle_tau)) * (1.0 - self.r)
        else:
            self.r = 0.0
        self.modes.append(self.mode)

    def boost(self, top: float, sl: float) -> float:
        """A boost's factor now: 1 .. top, smoothly with the extra ice, times the ending's ramp."""
        if self.r <= 0.0:
            return 1.0
        return 1.0 + (top - 1.0) * self.r * math.tanh(max(self.extra(sl), 0.0) / self.scale)

    def co2_target(self, target: float, sl: float) -> float:
        """The CO2 part's target (C) in an ending: the ice volume's (target) plus the release, at most
        the drawdown of the extra ice itself (co2_cool per 120 m of it, as Forcing's rule, but measured
        from the interglacial level and not clipped: the headroom a cold branch's clipped CO2 lacked)."""
        if self.r <= 0.0:
            return target
        room = self.p.co2_cool * max(self.extra(sl), 0.0) / 120.0
        return target + min(self.r * self.p.release * self.p.co2_cool, room)

    def summary(self) -> dict:
        lens = [x["kyr"] for x in self.endings if "kyr" in x]
        return {"on": self.on, "lat": None if self.lat is None else round(self.lat, 1),
                "scale_m": round(self.scale, 1), "sl_ig": round(self.sl_ig, 1),
                "sun": None if self.q is None else {"build": round(self.q_build, 1), "lo": round(self.q_lo, 1),
                                                    "hi": round(self.q_hi, 1)},
                "builds": self.builds, "endings": self.endings, "ending_kyr": lens,
                "backstops": self.backstops, "modes": self.modes}
