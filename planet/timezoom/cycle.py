"""The glacial index (PW-471): the ice-age cycle as a scripted cold-warm curve, paced by the planet's orbit.

The model can't (yet: PW-470) make ice ages emerge from its feedbacks, so the time zoom does what ice-sheet
modellers do when they can't simulate the cause either: it scripts how cold it is and lets the ice model
work out where the ice goes (the glacial index method: Greve 1997, Marshall et al. 2002). An index I(t)
runs from 0 (interglacial: the run's own climate, so the run's ice) to 1 (glacial maximum); the zoom's
global temperature is the run's minus I x the glacial cooling (cooling), polar-amplified as any global
change. The ice itself (balance, flow, margins, calving, isostasy) is the zoom's physics, untouched.

I(t) comes from a small conceptual model of global ice volume on the planet's own orbit (Paillard 1998's
three states; Huybers 2011: the insolation an ending needs falls with the time since the last one):

  between   I falls back to 0 (at 1/end_kyr per kyr: an ending's tail); a glacial starts building as soon
            as the summer sun at the cycling latitude falls below the build_q percentile of its own series.
  building  I grows at 1/build_kyr per kyr, faster in a weak summer and slower (stalling) in a strong one
            (build_orb: the orbit's pacing of the growth), up to 1. The glacial's age counts from its start.
  ending    entered once I >= end_min AND the summer sun beats a bar that falls with the glacial's age, from
            its series' bar_hi percentile at the start to bar_lo at glacial_kyr (the orbit picks the timing);
            I then falls to 0 over end_kyr, and it is between ice ages again.
  backstop  a glacial older than backstop x glacial_kyr ends at the next sunshine peak above the median
            (counted: only an orbit with almost no precession needs it).

Everything is relative to the planet: the sun's percentiles are of its own summer-insolation series (over
max(kyr, 800) kyr) at the cycling latitude, the mean latitude of the land poleward of its snowline
(snowline_land) in the hemisphere with more of it; an orbit with no swing (a 10-90 percentile spread under
1e-3 W/m2) never builds, so I stays 0. The glacial cooling scales with that land's share of the planet
(cooling).
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


def snowline_land(land: np.ndarray, ice: np.ndarray, t_sl: np.ndarray) -> np.ndarray:
    """The land a glacial can take: ice-free land (ice <= 1 m) whose annual mean temperature, brought to
    sea level by the lapse rate (t_sl), is below 0 C (poleward of the planet's snowline at sea level:
    where a cooler climate starts to keep its snow; Earth: Canada and Siberia north of ~50-55 N)."""
    return land & (ice <= 1.0) & (t_sl < 0.0)


def cycling_latitude(lat: np.ndarray, area: np.ndarray, sel: np.ndarray) -> float:
    """Where the ice age's ice grows: the cells in sel, in the hemisphere with more of their area, their
    area-weighted mean latitude (65 N if there are none)."""
    if not sel.any():
        return 65.0
    south = float(area[sel & (lat < 0)].sum()) > float(area[sel & (lat >= 0)].sum())
    s = sel & ((lat < 0) if south else (lat >= 0))
    return float((lat[s] * area[s]).sum() / area[s].sum())


def cooling(p, share: float) -> float:
    """The glacial maximum's global cooling (C, > 0): p.glacial_dt if set (>= 0), else glacial_cool at an
    Earth-like share of the planet (glacial_f) of land poleward of the snowline, in proportion to it (the
    more land a glacial can ice over, the more its albedo and CO2 drawdown cool), at most glacial_cap x."""
    if p.glacial_dt >= 0.0:
        return float(p.glacial_dt)
    return float(p.glacial_cool * min(share / p.glacial_f, p.glacial_cap))


class Index:
    """The glacial index over a time zoom of n_steps + 1 steps, precomputed from the orbit: .I[s_no]
    (0..1), .modes[s_no]; builds, endings (t, age, I at the start, length) and backstops."""

    def __init__(self, p, step: float, n_steps: int, tilt: float, ph, lat: float):
        self.p, self.step, self.lat = p, step, lat
        n = max(n_steps, int(round(800.0 / step))) + 2
        q = np.array([summer_sun(lat, orbit_at(i * step, p, tilt, ph)) for i in range(n)])
        pc = lambda x: float(np.percentile(q, 100 * x))
        self.q_build, self.q_hi, self.q_lo, self.q_mid = pc(p.build_q), pc(p.bar_hi), pc(p.bar_lo), pc(0.5)
        span = pc(0.9) - pc(0.1)
        self.q = q[:n_steps + 1]
        self.I = np.zeros(n_steps + 1)
        self.modes = np.zeros(n_steps + 1, np.int64)
        self.builds: list[float] = []
        self.endings: list[dict] = []
        self.backstops = 0
        if p.index != "on" or span < 1e-3:  # (an orbit with no swing: no ice ages; its q only has rounding noise)
            return
        mode, age, x = BETWEEN, p.ig_kyr, 0.0  # (the start: an interglacial)
        for i in range(n_steps + 1):
            self.I[i], self.modes[i] = x, mode  # (the step's state; then the next step's)
            t = i * step
            if mode == BETWEEN:
                age += step
                if q[i] < self.q_build and age >= p.ig_kyr:
                    mode, age = BUILDING, 0.0
                    self.builds.append(round(t, 1))
            elif mode == BUILDING:
                age += step
                g = 1.0 + p.build_orb * (self.q_mid - q[i]) / span
                x += (1.0 - x) * (1.0 - math.exp(-step / p.build_kyr * min(max(g, 0.0), 2.0)))
                bar = self.q_hi - (self.q_hi - self.q_lo) * min(age / p.glacial_kyr, 1.0)
                peak = q[i] >= q[max(i - 1, 0)] and q[i] > q[i + 1]
                sun = x >= p.end_min and q[i] >= bar
                stop = not sun and age > p.backstop * p.glacial_kyr and peak and q[i] > self.q_mid
                if sun or stop:
                    mode = ENDING
                    self.backstops += int(stop)
                    self.endings.append({"t": round(t, 1), "age_kyr": round(age, 1), "I": round(x, 2),
                                         "sun": round(float(q[i]), 1), "bar": round(float(bar), 1),
                                         "backstop": bool(stop)})
            else:
                x = max(x - step / p.end_kyr, 0.0)
                if x <= 0.0:
                    mode, age = BETWEEN, 0.0
                    self.endings[-1]["kyr"] = round(t - self.endings[-1]["t"] + step, 1)

    def summary(self) -> dict:
        ends = [e["t"] for e in self.endings]
        return {"on": self.p.index == "on", "lat": round(self.lat, 1),
                "sun": {"build": round(self.q_build, 1), "lo": round(self.q_lo, 1), "hi": round(self.q_hi, 1)},
                "builds": self.builds, "endings": self.endings, "cycle_kyr": np.diff(ends).round(1).tolist(),
                "backstops": self.backstops, "mean_I": round(float(self.I.mean()), 3)}
