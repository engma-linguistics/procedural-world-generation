"""The history's time steps: deep (Myr keyframes), glacial (the time zoom's frames), recent (centuries)."""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from ... import store as S, timeline as T
from ...geo import is_land


@dataclass
class Step:
    ago: float  # kyr before present (of this step's state)
    dt: float  # kyr since the previous step
    epoch: str  # deep | glacial | recent
    store: bool
    get: object  # () -> env dict
    stats: dict = field(default_factory=dict)


class StepsMixin:
    def _steps(self, glacial_every) -> list[Step]:
        ps, out = self.ps, []
        oldest = max(l.ago_kyr for l in self.lines)
        m = ps.run["meta"]
        now = ps.now
        # deep: the source run's keyframes before the time zoom's start
        if m.get("source_run") and m["source_run"] != "earth" and oldest > now:
            src = S.find_run(m["source_run"])
            run, arr = T.load_frames(src, ("elevation", "ice", "temperature", "precipitation", "climate", "tree_cover"))
            ts = np.array([f["t"] for f in run["frames"]])
            at = m["at_myr"]
            agos = (at - ts) * 1000 + now
            keep = np.flatnonzero((ts < at - 1e-6) & (agos <= oldest + 4000))
            if len(keep) and agos[keep].max() < oldest and keep.min() > 0:
                keep = np.r_[keep.min() - 1, keep]
            prev = None
            # a step at each keyframe, at each line's time between them (on the nearest keyframe's
            # world: 4 Myr keyframes would otherwise lump every split of those 4 Myr into one step)
            # and at the time zoom's start
            evs = sorted({l.ago_kyr for l in self.lines if now < l.ago_kyr <= agos[keep].max()} if len(keep) else set())
            sched = sorted({(float(agos[k]), int(k)) for k in keep} | {(float(a), int(keep[np.argmin(np.abs(agos[keep] - a))]))
                                                                        for a in evs} | {(float(now), int(keep[-1]))},
                           key=lambda x: -x[0]) if len(keep) else []
            for ago_k, k in sched:
                def get(k=k, run=run, arr=arr):
                    f = {n: ps.fine(T.frame(run, arr, n, k).astype(float), n == "climate") for n in ("elevation", "ice", "temperature",
                                                                                                    "precipitation", "climate")}
                    f["tree_cover"] = ps.fine(T.frame(run, arr, "tree_cover", k).astype(float)) if "tree_cover" in arr else np.zeros(len(f["ice"]))
                    f["land"] = is_land(f["elevation"], f["ice"])
                    f["elevation"] = np.where(f["ice"] > 0, np.maximum(f["elevation"], 0) + f["ice"], f["elevation"])
                    return f
                if prev is not None and prev - ago_k < 1e-6:
                    continue
                out.append(Step(ago_k, 4000.0 if prev is None else float(prev - ago_k), "deep", True, get,
                                {**run["frames"][k]["stats"], "epoch": "deep"}))
                prev = ago_k
        # glacial: the time zoom's frames before the recent window
        rstart = now + ps.start
        tz_ts = ps.ts[(ps.ts < rstart - 1e-6) & (now - ps.ts <= oldest + 2)]
        prev = out[-1].ago if out else None
        last_store = None
        for t in tz_ts:
            ago = now - t
            st = last_store is None or (last_store - ago) >= glacial_every - 1e-6
            if st:
                last_store = ago
            k = int(np.argmin(np.abs(ps.ts - t)))
            out.append(Step(float(ago), 2.0 if prev is None else float(prev - ago), "glacial", st,
                            lambda t=t: ps.fields(t - now, variability=False),
                            {**ps.run["frames"][k]["stats"], "epoch": "glacial"}))
            prev = ago
        # recent: century steps with the variability
        e = ps.params.every
        for t in ps.steps:
            ago = -float(t)
            st = abs(round(t / e) * e - t) < 1e-6
            out.append(Step(ago, ps.params.step if prev is not None else ps.params.step, "recent", st,
                            lambda t=float(t): ps.fields(t), {**ps.stats(float(t)), "epoch": "recent"}))
            prev = ago
        return out
