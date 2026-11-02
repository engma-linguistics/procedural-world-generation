"""The regional zoom build's landscape pass: the first glacier outline, the lakes, the drainage tools (lake outlets,
banks, falls, distributaries), the stream-power iterations, the final drainage and the shoreface.

Each stage takes the build's context (`ctx`, see regional.ZoomCtx), reads what the stages before it left on it,
and leaves its own results on it. A stage's docstring lists the context names it reads and writes. The helpers and
constants shared with the rest of the zoom are regional's (`RG.`).
"""
from __future__ import annotations

import time

import numpy as np

from ..surface import ROCK_K
from . import coast as ZC
from . import coastal as ZCL
from . import falls as ZFL
from . import kernels as ZK
from . import landforms as ZL
from . import regional as RG
from ..geo import smoothstep
from ..kernels import accumulate
from ..raster import box_mean


def first_glaciers(ctx):
    """The first glacier outline, on the target surface, for the lakes and the landscape pass to avoid.
    Reads: P, Pk, S, cov_f, edge, gc_sl, glacier_mask, gw_sl, h, ice, ice_n, inflow_pts, jitter_g, jul_f, land,
    lat_px, nx, ny, outlet, precip, res, sea, sp, tilt_w, world.
    Writes: edge, glacier, glacier_mask, ice, ice_n, ice_th, jitter_g, lat_px, outlet, precip, sea, tilt_w."""
    # --- landscape pass ----------------------------------------------------
    if ctx.match:  # (the neighbours' ground at their finished heights, PW-1301)
        from . import match as ZM
        ZM.hold(ctx)
    ctx.edge = np.zeros((ctx.ny, ctx.nx), bool)
    ctx.edge[0, :] = ctx.edge[-1, :] = ctx.edge[:, 0] = ctx.edge[:, -1] = True
    for p0, rr_ in ctx.inflow_pts:  # the edge next to where a river enters is land, not an outlet,
        r0, c0 = divmod(p0, ctx.nx)    # so the river can't drain straight back out of the region
        ctx.edge[max(r0 - rr_ - 3, 0):r0 + rr_ + 4, max(c0 - rr_ - 3, 0):c0 + rr_ + 4] = False
    ctx.edge = ctx.edge.ravel()
    ctx.sea = ~ctx.land
    ctx.outlet = ctx.sea | ctx.edge
    if ctx.match:  # (... held there, outlets of the landscape pass)
        ZM.hold_edge(ctx)
    ctx.precip = np.clip(np.nan_to_num(ctx.precip, nan=0.0), 0, None)
    ctx.ice = np.clip(np.nan_to_num(ctx.ice, nan=0.0), 0, None)
    # glaciers from each pixel's own climate (see glaciers()): a first
    # outline on the target surface (lakes and the landscape pass avoid and
    # smooth it), redrawn on the finished valleys after the landscape pass
    ctx.ice_n = ZK.fbm(ctx.Pk, 0.4 * ctx.sp, RG._octaves(0.4 * ctx.sp, 2 * ctx.res), 0.6, ctx.S + 5) / 0.17
    ctx.lat_px = np.degrees(np.arcsin(np.clip(ctx.P[:, 2], -1, 1)))
    ctx.tilt_w = float(ctx.world["meta"].get("params", {}).get("tilt", 23.4))

    def glacier_mask(hh, stop):
        _, rec_g, order_g = ZK.flood_d8(hh, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter_g)
        return RG.glaciers(hh, rec_g, order_g, ctx.land, stop, ctx.nx, ctx.ny, ctx.res, ctx.gw_sl, ctx.gc_sl, ctx.cov_f, ctx.precip, ctx.jul_f, ctx.ice,
                        ctx.lat_px, ctx.ice_n, ctx.tilt_w)
    ctx.glacier_mask = glacier_mask

    ctx.jitter_g = RG.tie_jitter(ctx.Pk, ctx.res, ctx.S + 63)
    ctx.glacier, ctx.ice_th = ctx.glacier_mask(ctx.h, ctx.sea)


def lakes(ctx):
    """Lakes where the coarse world has them: outlines, surface, depth, rims, and the runoff and loss that feed them.
    Reads: L, Pc, Pk, S, cexit, cgrad, clab, clvl, cqout, cx, cy, depth, e_c, edge, fr, g, glacier, h, inflow, lake,
    lake_c, lake_id, lakes, land, land_c, npx, nx, ny, outlet, own, precip, px, py, res, ring, ring_lvl, runoff,
    sel, sp, surf, surf_f.
    Writes: Kr, active, depth, h, idx, jitter, lake, lake_id, lake_loss, lake_seq, lakes, outlet, ring, ring_lvl,
    ring_px, srcg, srcq, surf, target."""
    # Lakes where the coarse world has them (a coarse lake cell is a lake
    # basin ~100 km across): outline like the coast, from a smoothed
    # lake/no-lake indicator plus fractal noise. The surface is the coarse
    # lake's water level (spill level, or the world's lake_level); the depth
    # follows the coarse fill depth (level - coarse ground), growing with
    # distance from the shore over a length set by the lake's size. In the
    # landscape pass a lake is an outlet held at its surface, so the land
    # around it drains in and is built up from the water; a one-pixel rim is
    # kept above the surface except along the outlet: the shore pixel
    # nearest the coarse lake's exit that drains away. Open lakes pass their
    # inflow (plus the rain on them) on at the outlet, closed ones keep it.
    min_px = max(3, int(np.ceil(30.0 / ctx.res**2)))  # ~30 km^2
    ctx.lake = np.zeros(ctx.npx, bool)
    ctx.surf = np.zeros(ctx.npx)  # lake surface
    ctx.depth = np.zeros(ctx.npx)
    ctx.lakes = []  # per fine lake: pixels, level, exit point (x, y) or None
    lk_c = ctx.lake_c[ctx.sel] & ctx.land_c
    if lk_c.any():
        dep_c = np.where(lk_c, ctx.clvl[np.maximum(ctx.clab[ctx.sel], 0)] - ctx.e_c, 0.0)
        lind, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, np.column_stack([np.where(lk_c, 1.0, -1.0), dep_c]),
                                  np.column_stack([ctx.land_c, lk_c]).astype(float), 0.42 * ctx.sp)
        lake_n = ZK.fbm(ctx.Pc, 0.5 * ctx.sp, RG._octaves(0.5 * ctx.sp, 2 * ctx.res), 0.6, ctx.S + 8) / 0.15
        cand = ctx.land & ~ctx.edge & ~ctx.glacier & (np.nan_to_num(lind[:, 0], nan=-1.0) + 0.2 * lake_n > 0.1)
        if ctx.match:  # (the neighbours' lake outlines where they weigh over a half, on held ground too, PW-1301)
            from . import match as ZM
            cand = ZM.lakes(ctx, cand)
        lab, sizes = ZK.label_components(cand, ctx.nx, ctx.ny)
        pl = np.flatnonzero(lab >= 0)
        pl = pl[sizes[lab[pl]] >= min_px]
        pl = pl[np.argsort(lab[pl], kind="stable")]
        lk_cells = ctx.sel[lk_c]
        for pix in np.split(pl, np.flatnonzero(np.diff(lab[pl])) + 1) if len(pl) else []:
            cl = ctx.clab[ctx.own[pix]]
            cl = cl[cl >= 0]
            if len(cl):
                c = np.bincount(cl).argmax()
            else:  # the outline drifted off the coarse lake cells: nearest one
                c = ctx.clab[lk_cells[np.argmin(np.hypot(ctx.cx[lk_c] - ctx.px[pix].mean(), ctx.cy[lk_c] - ctx.py[pix].mean()))]]
            ex = None
            if ctx.cexit[c] >= 0:
                (a,), (b,) = ctx.fr.to_plane(ctx.g.centers[ctx.cexit[c]][None])
                ex = (a, b)
            ctx.lake[pix] = True
            ctx.surf[pix] = ctx.clvl[c]
            ctx.lakes.append({"px": pix, "level": float(ctx.clvl[c]), "exit": ex, "cl": int(c), "closed": ex is None,
                          "grad": max(RG.RAPIDS_GRAD, float(ctx.cgrad[c])), "q_out": float(ctx.cqout[c]) if ex is not None else 0.0})
        # A closed lake's smaller fragments (its outline broken up by the
        # noise or the coarse mask) pass their water on to its biggest one
        # instead of swallowing their rivers (the biggest stays closed).
        main = {}
        for j, lk in enumerate(ctx.lakes):
            m = main.get(lk["cl"])
            if lk["exit"] is None and (m is None or len(lk["px"]) > len(ctx.lakes[m]["px"])):
                main[lk["cl"]] = j
        for j, lk in enumerate(ctx.lakes):
            m = main.get(lk["cl"])
            if lk["exit"] is None and m is not None and m != j:
                mp = ctx.lakes[m]["px"]
                k = mp[np.argmin(np.hypot(ctx.px[mp] - ctx.px[lk["px"]].mean(), ctx.py[mp] - ctx.py[lk["px"]].mean()))]
                lk["exit"] = (float(ctx.px[k]), float(ctx.py[k]))
    if ctx.lakes:
        ds = ZK.inside_distance(ctx.lake, ctx.nx, ctx.ny) * ctx.res  # km to the shore
        dc = np.nan_to_num(lind[:, 1], nan=0.0)
        nz = ZK.fbm(ctx.Pk, 0.3 * ctx.sp, RG._octaves(0.3 * ctx.sp, 2 * ctx.res), 0.55, ctx.S + 9) / 0.17
        for lk in ctx.lakes:
            pix = lk["px"]
            dcm = np.maximum(dc[pix], 2.0)
            ell = np.clip(0.25 * ds[pix].max(), 2 * ctx.res, 80.0)
            d0 = dcm * (1 - np.exp(-ds[pix] / ell)) * np.clip(1 + 0.3 * nz[pix], 0.4, 1.6)
            # about the coarse mean depth overall
            ctx.depth[pix] = np.maximum(np.clip(dcm.mean() / max(d0.mean(), 1e-6), 0.7, 3.0) * d0, 0.5)
        ctx.h = np.where(ctx.lake, ctx.surf, ctx.h)
        ctx.outlet = ctx.outlet | ctx.lake
    ctx.lake_id = np.full(ctx.npx, -1)
    for j, lk in enumerate(ctx.lakes):
        ctx.lake_id[lk["px"]] = j
    # the rim: land next to a lake (the highest one, if it touches two)
    ctx.ring_lvl, ring_id = np.full(ctx.npx, -np.inf), np.full(ctx.npx, -1)
    l2, id2 = np.where(ctx.lake, ctx.surf, -np.inf).reshape(ctx.ny, ctx.nx), ctx.lake_id.reshape(ctx.ny, ctx.nx)
    for dr in (-1, 0, 1):
        for dcol in (-1, 0, 1):
            v, i2 = RG._shift(l2, dr, dcol, -np.inf).ravel(), RG._shift(id2, dr, dcol, -1).ravel()
            ring_id = np.where(v > ctx.ring_lvl, i2, ring_id)
            ctx.ring_lvl = np.maximum(ctx.ring_lvl, v)
    ctx.ring = ctx.land & ~ctx.lake & ~ctx.edge & (ring_id >= 0)
    ctx.ring_px = [np.flatnonzero(ctx.ring & (ring_id == j)) for j in range(len(ctx.lakes))]
    ctx.lake_seq = sorted(range(len(ctx.lakes)), key=lambda j: -ctx.lakes[j]["level"])  # upstream lakes first
    ctx.srcq = ctx.runoff / 1000.0 * ctx.res * ctx.res + ctx.inflow  # km^2 m/yr per pixel
    # open water's net evaporation (beyond the land's, which runoff already
    # takes off), m/yr: a lake loses it over its area before passing its water
    # on (as the coarse world's lakes do, hydrology.lakes; PW-271), and a
    # landform basin's water balance weighs its inflow against it
    if "lake_evap" in ctx.L and "evaporation" in ctx.L:
        ls_c = np.asarray(ctx.L["lake_evap"], float)[ctx.sel] - np.asarray(ctx.L["evaporation"], float)[ctx.sel]
    else:
        ls_c = np.full(len(ctx.sel), RG.LF_LOSS_MM)
    fv, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, np.maximum(ls_c, 0.0)[:, None], ctx.land_c[:, None].astype(float), 0.5 * ctx.sp)
    ctx.lake_loss = np.nan_to_num(fv[:, 0]) / 1000.0
    # The landscape's shape (the stream-power grading, creep, the landform
    # classes' valleys) follows the rain-weighted drainage area instead: a
    # desert's wadis are cut by its rare floods, which mean runoff (~0
    # there) doesn't measure. The pass is calibrated to the coarse heights
    # anyway (C), so only the relative weights matter.
    ctx.srcg = ctx.precip / 1000.0 * ctx.res * ctx.res + ctx.inflow
    ctx.Kr = ROCK_K[np.minimum(ctx.surf_f, len(ROCK_K) - 1)]
    ctx.jitter = RG.tie_jitter(ctx.Pk, ctx.res, ctx.S + 61)
    ctx.active = ctx.land & ~ctx.edge & ~ctx.lake
    ctx.idx = np.arange(ctx.npx)
    ctx.target = ctx.h.copy()


def drainage_tools(ctx):
    """The landscape pass's tools (lake outlets, banks, rims, falls, rerouting, routing, distributaries, the slope fit)
    as closures on the context.
    Reads: BR, active, banks, base, bottom, branch, cap, chain_km, kpix, kps, lake, lake_id, lake_loss,
    lake_outlets, lake_seq, lakes, npx, nx, ny, outlet, ov_dst, ov_src, pin_dst, pin_pairs, pin_src, px, py,
    q_course, rapids, region, res, ring, ring_lvl, ring_px, route, s_pix, sea, seed, splits, srcq, target, trunk_px,
    vpin, wR_f.
    Writes: BR, banks, branch, chain_km, lake_outlets, make_branches, ov_dst, ov_src, pin_dst, pin_src, place_falls,
    rapids, reroute, rims, route, splits, trunk_px."""

    def lake_outlets(rec):
        """Per lake, the rim pixel nearest the coarse exit that drains away (-1: none)."""
        outs = np.full(len(ctx.lakes), -1)
        for j, lk in enumerate(ctx.lakes):
            c = ctx.ring_px[j]
            if lk["exit"] is None or not len(c):
                continue
            c = c[(rec[c] >= 0) & ~ctx.lake[np.maximum(rec[c], 0)]]
            if len(c):
                outs[j] = c[np.argmin(np.hypot(ctx.px[c] - lk["exit"][0], ctx.py[c] - lk["exit"][1]))]
        return outs
    ctx.lake_outlets = lake_outlets

    ctx.rapids = np.zeros(ctx.npx, bool)  # below a lake's outlet (rims())

    def banks(ch, z, take_max):
        """Valley sides along a held river course (pixels ch at heights z):
        per pixel within BANK_KM (at least 2 px) of it, the height of the
        nearest course pixel (the highest, or lowest, of equally near ones)
        + 0.5 m; beyond that falling off at BANK_SIDE_GRAD m/km, out to at
        most 20 km. Returns (pixels, floor), course pixels and inactive
        ones left out."""
        wk = max(RG.BANK_KM, 2 * ctx.res)
        wmax = wk + 20.0
        kk = int(np.ceil(wmax / ctx.res))
        r0, c0 = np.divmod(ch, ctx.nx)
        bd = np.full(ctx.npx, np.inf)
        bf = np.full(ctx.npx, -np.inf if take_max else np.inf)
        for d, dr, dc in sorted((ctx.res * np.hypot(dr, dc), dr, dc) for dr in range(-kk, kk + 1) for dc in range(-kk, kk + 1)):
            if d > wmax:
                break
            r, c = r0 + dr, c0 + dc
            inr = (r >= 0) & (r < ctx.ny) & (c >= 0) & (c < ctx.nx)
            win, f = r[inr] * ctx.nx + c[inr], z[inr]
            a = ctx.active[win] & (bd[win] >= d - 1e-9)
            bd[win[a]] = d
            (np.maximum if take_max else np.minimum).at(bf, win[a], f[a])
        near = np.flatnonzero(np.isfinite(bd) & (bd > 0))
        fz = bf[near] + 0.5 - RG.BANK_SIDE_GRAD * np.maximum(bd[near] - wk, 0.0)
        return near, fz
    ctx.banks = banks

    def rims(rec, outs, step):
        """Per-pixel floor (rims above their lake) and cap (outlet channels
        below it) for the landscape integration."""
        fl, cp = np.full(ctx.npx, 0.5), ctx.cap.copy()
        fl[ctx.ring] = ctx.ring_lvl[ctx.ring] + 0.5
        ctx.rapids[:] = False
        for j, o in enumerate(outs):
            if o >= 0:
                ch = ZK.chain(rec, o)
                fl[ch] = 0.5  # no rim along the outflow
                cp[ch] = np.minimum(cp[ch], ctx.lakes[j]["level"] - 0.3)
                # Below the sill the ground steps down gradually: the outflow
                # lies no more than G * s below the lake, s km down the river
                # (rapids), out to the first fall placed on the outflow,
                # instead of a cliff down to a river graded up from far below.
                # G is the coarse outflow's own descent (outflow_grad), at
                # least RAPIDS_GRAD: a mountain lake's outflow cascades down
                # its valley rather than standing above it on a gentle ramp
                # (PW-123). Its banks stand a little above the river beside them
                # (or the water just finds a neighbour that drops away): banks().
                lv, gr = ctx.lakes[j]["level"] - 0.3, ctx.lakes[j]["grad"]
                s_ch = np.concatenate([[0.0], np.cumsum(ctx.chain_km(ch))])
                st_ = np.flatnonzero(step[ch] > 0)
                rkm = min(lv / gr, 150.0, s_ch[st_[0]] if len(st_) else np.inf)
                ok = s_ch <= rkm
                fz = lv - gr * s_ch[ok]
                near, fz_ = ctx.banks(ch[ok], fz, True)
                near, fz_ = np.concatenate([ch[ok], near]), np.concatenate([fz, fz_])
                a = ctx.active[near]
                near, fz_ = near[a], fz_[a]
                # (never above the coarse ground: where that drops away fast, so does the river)
                fz_ = np.minimum(fz_, np.maximum(ctx.base[near], ctx.target[near]))
                fl[near] = np.maximum(fl[near], fz_)
                ctx.rapids[near] = True
        return fl, cp
    ctx.rims = rims

    def chain_km(ch):
        """Length of each link of a receiver chain, km."""
        a, b = ch[:-1], ch[1:]
        return ctx.res * np.where((a % ctx.nx != b % ctx.nx) & (a // ctx.nx != b // ctx.nx), 1.4142, 1.0)
    ctx.chain_km = chain_km

    def place_falls(rec, Q, hprev):
        """Follow each reach with falls down the river as it runs now: from
        the first pixel of its course carrying the coarse river's water
        (>= FALLS_MIN_SHARE x the coarse discharge; else the most upstream
        pixel in the valley bottom with >= 0.3x), down the receivers (pinned along the reach's
        course: reroute), with the arc length along
        the reach (of the nearest polyline point) taken as a running maximum
        so it only grows. The river gets the staircase floor at that arc
        length, and the lip of each fall is where it crosses the fall's step.
        Returns (chain pixels, their floor, step height at each lip, gorge
        rim floor per pixel, cliff mask (lips, feet, gorges and their walls:
        no creep), [(lip, step, knickpoint)]). The gorge runs from the foot
        of the main fall for its length; the land beside it is held at the
        lip's level (hprev: the last iteration's surface), falling off by a
        quarter of the fall towards the gorge mouth, so its walls are cliffs
        and side streams join it in hanging falls."""
        step, flg, cliff, lips = np.zeros(ctx.npx), np.full(ctx.npx, -np.inf), np.zeros(ctx.npx, bool), []
        c_idx, c_val, ends, end_z, end_k = [], [], [], [], []
        rv = (ctx.kpix >= 0) & ctx.bottom & (rec >= 0) & (Q >= 0.3 * ctx.q_course) & ctx.active  # (starting in the valley bottom)
        # (on the pinned course itself, a fraction of that will do: the coarse
        # discharge is the cell's whole, and near the head of a reach, or of a
        # river rising in the region, the fine river carries much less)
        rv_c = (ctx.kpix >= 0) & (rec >= 0) & (Q >= RG.FALLS_MIN_SHARE * ctx.q_course) & ctx.active
        inner3 = np.zeros((ctx.ny, ctx.nx), bool)
        inner3[3:-3, 3:-3] = True
        inner3 = inner3.ravel()
        for k_, kp in enumerate(ctx.kps):
            # (on its pinned course if the water is there: another river in
            # the corridor, e.g. a parallel reach, mustn't be taken for it)
            # (and not within 3 px of the region's edge, where rivers come in:
            # a course running along the edge may drain off it there, out of
            # the region, and the reach would be followed for a pixel or two)
            cp_ = kp["course_px"]
            r_k = cp_[rv_c[cp_] & (ctx.kpix[cp_] == k_) & inner3[cp_]]
            if not len(r_k):
                r_k = np.flatnonzero(rv & (ctx.kpix == k_))
                if not len(r_k):
                    continue
                r_k = r_k[np.argsort(ctx.s_pix[r_k])]
            ch = ZK.chain(rec, int(r_k[0]))
            mine = ctx.kpix[ch] == k_
            ch = ch[:np.flatnonzero(mine)[-1] + 1]
            # (not on into a delta's distributaries: below its apex the plain
            # shapes the channels, PW-363)
            ch = ch[:np.argmax(ctx.branch[ch])] if ctx.branch[ch].any() else ch
            ch = ch[ctx.active[ch]]
            if not len(ch):
                continue
            ends.append(int(ch[-1]))
            # (the arc length along the course itself where the river is on it:
            # the nearest polyline point jumps where a meander comes back near itself)
            s_ch = np.where(ctx.kpix[ch] == k_, ctx.s_pix[ch], 0.0)
            on_c = np.isin(ch, kp["course_px"])
            if on_c.any():
                o = np.argsort(kp["course_px"])
                s_ch[on_c] = kp["course_s"][o[np.searchsorted(kp["course_px"], ch[on_c], sorter=o)]]
            sv = np.maximum.accumulate(s_ch)
            c_idx.append(ch)
            c_val.append(RG.stair_z(kp, sv))
            end_z.append(float(c_val[-1][-1]))
            end_k.append(k_)
            for st in kp["steps"]:
                j = np.flatnonzero(sv >= st["s"])
                if not len(j) or j[0] == 0:
                    continue
                lip = int(ch[j[0] - 1])
                foot = int(rec[lip])
                step[lip] = st["h"]
                cliff[[lip, foot]] = True
                lips.append((lip, st, kp))
                if hprev is None:
                    continue
                # (a fall without a gorge still gets walls beside its foot)
                g = ZK.chain(rec, foot)
                sg = np.concatenate([[0.0], np.cumsum(ctx.chain_km(g))])
                g, sg = g[sg <= st["gorge_km"]], sg[sg <= st["gorge_km"]]
                g, sg = g[ctx.active[g]], sg[ctx.active[g]]
                if not len(g):
                    continue
                top = hprev[lip] - 0.25 * st["h"] * sg / max(st["gorge_km"], 1e-6)
                cliff[g] = True
                r, cc = np.divmod(g, ctx.nx)
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nb = np.clip(r + dr, 0, ctx.ny - 1) * ctx.nx + np.clip(cc + dc, 0, ctx.nx - 1)
                        ok = ctx.active[nb] & (Q[nb] < 0.3 * Q[lip]) & (nb != lip)
                        np.maximum.at(flg, nb[ok], top[ok])
                        cliff[nb[ok]] = True
        c_idx = np.concatenate(c_idx) if c_idx else np.zeros(0, np.int64)
        c_val = np.concatenate(c_val) if c_val else np.zeros(0)
        if len(c_idx):
            # Banks: the ground beside the river on a reach with falls stands
            # above it (the lowest of the nearest river pixels), so the river
            # stays in its course down to the lip instead of leaving it
            # (sideways, down a bare step) wherever the land next to it drains
            # lower, and doesn't run perched above the land beside it: valley
            # sides a few km wide (banks()). Not on the river itself, nor on
            # its course below the reach.
            on = np.zeros(ctx.npx, bool)
            on[c_idx] = True
            for e_ in ends:
                on[ZK.chain(rec, e_)] = True
            b, fz = ctx.banks(c_idx, c_val, False)
            # (nor on other rivers: a bigger river nearby, or another coarse
            # river's valley bottom, isn't lifted onto this one's banks)
            keep = ~on[b] & ~(ctx.bottom[b] & (ctx.kpix[b] < 0)) & (Q[b] * RG.KM2_M_PER_YR_TO_M3S < RG.BANK_MAX_Q)
            b, fz = b[keep], fz[keep]
            flg[b] = np.maximum(flg[b], fz)
            cliff[c_idx] = True  # the course and its banks don't creep either
            r, cc = np.divmod(c_idx, ctx.nx)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    ok = (r + dr >= 0) & (r + dr < ctx.ny) & (cc + dc >= 0) & (cc + dc < ctx.nx)
                    nb = ((r + dr) * ctx.nx + cc + dc)[ok]
                    cliff[nb[ctx.active[nb] & ~on[nb]]] = True
        if lips:
            flg[[lp for lp, _, _ in lips]] = -np.inf
        # below each reach the river runs no higher than the foot of its
        # staircase (else it holds the reach's lower falls up: they vanish)
        # (until it joins a bigger river, or another reach with falls)
        below = []
        for e_, k_ in zip(ends, end_k):
            g = ZK.chain(rec, e_)[1:]
            stop = (Q[g] > 1.5 * Q[e_]) | ((ctx.kpix[g] >= 0) & (ctx.kpix[g] != k_))
            below.append(g[:np.flatnonzero(stop)[0]] if stop.any() else g)
        b_val = np.concatenate([np.full(len(g), z_) for g, z_ in zip(below, end_z)]) if below else np.zeros(0)
        below = np.concatenate(below) if below else np.zeros(0, np.int64)
        return c_idx, c_val, step, flg, cliff, lips, (below, b_val)
    ctx.place_falls = place_falls

    # the courses of reaches with falls (pinned receivers), on open ground
    pin = {a: b for a, b in ctx.pin_pairs if ctx.active[a] and ctx.active[b]}
    ctx.pin_src, ctx.pin_dst = np.array(list(pin), dtype=np.int64), np.array(list(pin.values()), dtype=np.int64)

    def reroute(rec, order):
        """Pin the courses of reaches with falls, then apply the distributary
        receivers (each only if it leaves the network acyclic)."""
        def pin(rec, order, src, dst):
            """rec with src -> dst pinned, but for the pixels of any loop
            that makes (a course draining back into itself): those unpinned.
            Returns (rec, order, all pinned?)."""
            n0 = len(src)
            while len(src):
                r2 = rec.copy()
                r2[src] = dst
                o2 = ZK.receiver_order(r2)
                if len(o2) == ctx.npx:
                    return r2, o2, len(src) == n0
                done = np.zeros(ctx.npx, bool)
                done[o2] = True
                walk, i = {}, int(np.flatnonzero(~done)[0])
                while i not in walk:
                    walk[i] = len(walk)
                    i = int(r2[i])
                loop = list(walk)[walk[i]:]
                keep = ~np.isin(src, loop)
                if keep.all():
                    break
                src, dst = src[keep], dst[keep]
            return rec, order, False

        rec, order, _ = pin(rec, order, ctx.pin_src, ctx.pin_dst)
        if not len(ctx.ov_src):
            return rec, order, False
        # (the distributaries were laid out on an earlier network: where one
        # now closes a loop, only that loop's pixels are let go)
        r2, o2, _ = pin(rec, order, ctx.ov_src, ctx.ov_dst)
        return (r2, o2, True) if r2 is not rec else (rec, order, False)
    ctx.reroute = reroute

    def route(src, rec, order, outs, split_ok, loss=None, water=True):
        """Accumulate src downstream, then pass each open lake's total on at
        its outlet (less loss x its area, floored at 0: open water's
        evaporation) and divide the water at distributary splits. Returns q
        and each lake's total inflow (its own rain included). With water
        (not for a drainage area), a coarse lake's outlet passes on at least
        the world's outflow of that lake: the zoom sees only the part of a
        big lake's catchment inside it, and only the rivers entering the
        region bring in the rest (PW-060). The outlet is that of the lake's
        fragment nearest its coarse exit, taken last of its level."""
        q = accumulate(rec, order, src)
        tot = np.zeros(len(ctx.lakes))
        main = {}  # coarse lake -> its fine fragment draining to its exit
        for j, lk in enumerate(ctx.lakes):
            if water and outs[j] >= 0 and lk["q_out"] > 0 and not lk["closed"]:
                d_ = np.hypot(ctx.px[outs[j]] - lk["exit"][0], ctx.py[outs[j]] - lk["exit"][1])
                if lk["cl"] not in main or d_ < main[lk["cl"]][1]:
                    main[lk["cl"]] = (j, d_)
        mains = {j for j, _ in main.values()}
        # (upstream lakes first: by the number of lakes below each, as the
        # outflows chain; a coarse lake's fragments share one level)
        below = {}
        for j in range(len(ctx.lakes)):
            if outs[j] >= 0:
                end = ZK.chain(rec, outs[j])[-1]
                below[j] = int(ctx.lake_id[end]) if ctx.lake[end] and ctx.lake_id[end] != j else -1
        depth = {}

        def n_below(j, hops=0):
            if j not in depth:
                k = below.get(j, -1)
                depth[j] = 0 if k < 0 or hops > len(ctx.lakes) else 1 + n_below(k, hops + 1)
            return depth[j]
        passed = {}  # coarse lake -> what its other fragments passed on
        for j in sorted(ctx.lake_seq, key=lambda j: (-n_below(j), -ctx.lakes[j]["level"], j in mains)):
            tot[j] = q[ctx.lakes[j]["px"]].sum()
            if outs[j] >= 0:
                lost = 0.0 if loss is None else loss[ctx.lakes[j]["px"]].sum() * ctx.res * ctx.res
                out = max(tot[j] - lost, 0.0)
                cl_ = ctx.lakes[j]["cl"]
                if j in mains:
                    out = max(out, ctx.lakes[j]["q_out"] - passed.get(cl_, 0.0))
                elif cl_ in main:  # (not one draining into the main fragment: its water is in the main's)
                    k, hops = below.get(j, -1), 0
                    while k >= 0 and k != main[cl_][0] and hops <= len(ctx.lakes):
                        k, hops = below.get(k, -1), hops + 1
                    if k != main[cl_][0]:
                        passed[cl_] = passed.get(cl_, 0.0) + out
                ZK.add_chain(q, rec, outs[j], out)
        if split_ok:
            for s, kids, f in ctx.splits:
                qs = q[s]
                ZK.add_chain(q, rec, kids[0], -(1 - f[0]) * qs)
                for c, fk in zip(kids[1:], f[1:]):
                    ZK.add_chain(q, rec, c, fk * qs)
        return q, tot
    ctx.route = route

    # --- distributaries --------------------------------------------------
    # Below a delta apex (on the main river, 0.6 R up from its mouth) the
    # river splits into 2-6 branches that fan out to points on the coast
    # around the main mouth: a binary tree of wandering paths, each branch
    # taking a share of the water. D8 routing gives every pixel a single
    # receiver, so the branches are pinned as receiver overrides and the
    # shares are added down each branch (route); the landscape pass then
    # builds the plain around them. Laid out once the drainage network of
    # the landscape pass has settled a bit (a third of the way through).
    ctx.ov_src = ctx.ov_dst = np.zeros(0, np.int64)
    ctx.splits = []
    ctx.trunk_px = []  # (the main channels pinned down to each apex)
    ctx.branch = np.zeros(ctx.npx, bool)  # the distributaries below the apexes (PW-363)

    # (the distributaries laid so far: overrides, splits, pixels taken)
    ctx.BR = {"ov": {}, "splits": [], "via": {}, "assigned": np.zeros(ctx.npx, bool), "blocked": np.zeros(ctx.npx, bool),
          "rng": np.random.default_rng(ctx.seed + 7)}

    def make_branches(rec0, order0, todo):
        """Receiver overrides (src, dst) and splits for the deltas, laid out
        on the drainage network (rec0, order0) of a landscape iteration: the
        deltas `todo` added to those laid before."""
        ov, splits, via_map = ctx.BR["ov"], ctx.BR["splits"], ctx.BR["via"]  # (via_map: a finger tip's goal pixel -> the finger's axis)
        reached = set()  # (the goals a branch of their own runs out to the sea at)
        top_z = [np.inf]  # (the highest ground a delta's branches may cross: set per delta)
        score = ctx.route(ctx.srcq, rec0, order0, ctx.lake_outlets(rec0), False, ctx.lake_loss)[0]
        assigned = ctx.BR["assigned"]
        rng = ctx.BR["rng"]

        # Each branch heads for its own point on the coast, spread around the
        # main mouth, along a smooth curve rasterised onto the pixels (any
        # direction, not D8's eight): bowed to one side and wandering, less
        # on a river-dominated delta, whose channels run straighter between
        # their levees; a finger's branch runs on out along the finger's axis.
        coast = np.zeros(ctx.npx, bool)  # land next to the sea
        for dr, dcol in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            coast |= ctx.active & RG._shift(ctx.sea.reshape(ctx.ny, ctx.nx), dr, dcol, False).ravel()
        nb8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        def curve(p0, end, wr, k=0):
            """A distributary's course (km) from p0 to end: a bow of ~N(0,
            12%) of its length to one side and a wiggle of ~25 km wavelength."""
            v = end - p0
            L = float(np.hypot(*v))
            if L < ctx.res:
                return np.array([p0, end])
            nrm = np.array([-v[1], v[0]]) / L
            tt = np.linspace(0.0, 1.0, max(8, int(2 * L / ctx.res)))
            bow = rng.normal(0.0, 0.12 * (1 + 0.6 * k)) * (1 - 0.5 * wr)  # (wider on each retry)
            wig = 0.04 * (1 - 0.6 * wr) * np.sin(2 * np.pi * tt * L / rng.uniform(15.0, 35.0) + rng.uniform(0, 2 * np.pi))
            off = L * (4 * bow * tt * (1 - tt) + wig * np.sin(np.pi * tt))
            return p0 + tt[:, None] * v + off[:, None] * nrm

        def walk(s0, line, nsteps, blocked):
            """Pixels (start excluded) from s0 along the polyline (km), a
            step at a time: towards a point a little ahead on it (so the
            channel follows the curve in any direction), every step nearer
            its far end (so it arrives and can't loop; the line runs on out
            into the sea), round high ground and the other branches (joining
            one only where that leads on to the sea, not back up its own
            course). It stops at the sea (or a lake, the region's edge),
            another branch, nsteps, or where it can't get on. Returns (the
            pixels, did it run clear?)."""
            seg = np.hypot(*np.diff(line, axis=0).T)
            s_ = np.concatenate([[0.0], np.cumsum(seg)])
            t_ = np.arange(0.0, s_[-1] + 1e-9, 0.5 * ctx.res)
            pts = np.column_stack([np.interp(t_, s_, line[:, 0]), np.interp(t_, s_, line[:, 1])])
            gx_, gy_ = pts[-1]
            out, seen, i, j = [], {int(s0)}, int(s0), 0
            top_ = top_z[0]

            def joins(q):
                """Does joining the branch at q lead on to the sea, not back
                through s0 (its own upstream: a loop)?"""
                p, n_ = int(q), 0
                while p in ov and n_ < ctx.npx:
                    if p == s0 or p in seen:
                        return False
                    p, n_ = int(ov[p]), n_ + 1
                return p != s0 and p not in seen

            while len(out) < nsteps:
                r0, c0 = divmod(i, ctx.nx)
                tx, ty = pts[min(j + 4, len(pts) - 1)]  # (2 px ahead)
                th = np.arctan2(ty - ctx.py[i], tx - ctx.px[i])
                d0 = np.hypot(ctx.px[i] - gx_, ctx.py[i] - gy_)
                best, bs = -1, -9.0
                for a, b in nb8:
                    if not (0 <= r0 + a < ctx.ny and 0 <= c0 + b < ctx.nx):
                        continue
                    q = (r0 + a) * ctx.nx + c0 + b
                    if q in seen or blocked[q] or (assigned[q] and not joins(q)):
                        continue
                    if ctx.base[q] > top_ and not ctx.outlet[q]:
                        continue  # (no climbing: a pinned channel uphill lifts its whole course above the plain)
                    dq = np.hypot(ctx.px[q] - gx_, ctx.py[q] - gy_)
                    if len(out) < 3:  # leave the split point: on fresh ground, not much further away
                        if assigned[q] or dq > d0 + ctx.res:
                            continue
                    elif dq >= d0 and not ctx.outlet[q]:
                        continue
                    sc = np.cos(np.arctan2(-a, b) - th) - (3.0 if assigned[q] else 0.0)
                    if sc > bs:
                        best, bs = q, sc
                if best < 0:
                    return out, False
                out.append(best)
                seen.add(best)
                if assigned[best]:
                    return out, False
                if ctx.outlet[best]:
                    return out, True
                i = best
                w = pts[j:j + 12]
                j += int(np.argmin(np.hypot(w[:, 0] - ctx.px[i], w[:, 1] - ctx.py[i])))
            return out, True

        def toward(s0, gx, gy, nsteps, blocked, via=None, side=0):
            """Pixels (start excluded) along a curve from s0 towards (gx, gy)
            km (and on along `via`, a finger's axis, if given), at most
            nsteps, on past its end into the sea (walk). Of a few bows, the
            first that runs clear of the other branches and the high ground,
            else the one that gets furthest. side (-1, +1; 0: none): a
            split's child leaves it turned ~35 deg to its own side of the fan
            (clockwise -1), away from its sibling."""
            p0 = np.array([ctx.px[s0], ctx.py[s0]])
            end = np.array([gx, gy]) if via is None else np.asarray(via[0], float)
            p1 = p0
            if side and np.hypot(*(end - p0)) > 6 * ctx.res:
                d_ = (end - p0) / np.hypot(*(end - p0))
                a_ = np.radians(35.0) * side
                p1 = p0 + 2.5 * ctx.res * np.array([d_[0] * np.cos(a_) - d_[1] * np.sin(a_),
                                                d_[0] * np.sin(a_) + d_[1] * np.cos(a_)])
            best = []
            for k in range(4):
                line = curve(p1, end, float(ctx.wR_f[s0]), k)
                if p1 is not p0:
                    line = np.concatenate([[p0], line])
                if via is not None:
                    line = np.concatenate([line, np.asarray(via[1:], float)])
                e = line[-1] - line[-2]
                line = np.concatenate([line, [line[-1] + 30 * ctx.res * e / max(float(np.hypot(*e)), 1e-9)]])
                out, clear = walk(s0, line, nsteps, blocked)
                if clear and out:
                    return out
                if len(out) > len(best):
                    best = out
            return best

        def commit(start, pix, blocked):
            """Pin pix as a channel after start; it ends at the sea (or a lake,
            or the region edge) or where it joins another branch. Returns
            (first pixel, last pixel, open end?)."""
            prev, first = start, -1
            for p in pix:
                if blocked[p]:
                    return first, prev, True
                if prev != start:
                    ov[prev] = p
                if first < 0:
                    first = p
                if ctx.outlet[p] or assigned[p]:
                    return first, p, False
                assigned[p] = True
                prev = p
            return first, prev, True

        def grow(s, goals, seg, blocked):
            """Split at pixel s into two groups of coast goals (one each if
            only two); a group heads for its goals' mean for `seg` pixels,
            then splits again. A branch none of whose channels reaches the
            sea or another branch (stuck inland: high ground in the way) is
            taken back: its open end would drain back into the delta (a
            loop, and no distributaries at all). Returns: any kept?"""
            k0 = len(splits)
            splits.append(None)
            m = max(len(goals) // 2, 1)
            groups = [goals[:m], goals[m:]] if len(goals) > 1 else [goals]
            share = np.array([len(gp) for gp in groups], float) * rng.uniform(0.75, 1.25, len(groups))
            kids, fr_ = [], []
            for gi, (gp, f) in enumerate(zip(groups, share)):
                gx, gy = np.mean([ctx.px[q] for q in gp]), np.mean([ctx.py[q] for q in gp])
                # (turned to its side of the fan; failing that, straight off: the side may be high ground)
                for side in dict.fromkeys(((2 * gi - 1) if len(groups) > 1 else 0, 0)):
                    pix = toward(s, gx, gy, ctx.npx if len(gp) == 1 else seg, blocked,
                                 via_map.get(gp[0]) if len(gp) == 1 else None, side)
                    snap_k = (dict(ov), assigned.copy(), len(splits))
                    first, last, open_ = commit(s, pix, blocked)
                    if first < 0:
                        continue
                    if open_ and not (len(gp) > 1 and grow(last, gp, seg, blocked)):
                        ov.clear()
                        ov.update(snap_k[0])
                        assigned[:] = snap_k[1]
                        del splits[snap_k[2]:]
                        continue
                    kids.append(first)
                    fr_.append(f)
                    if len(gp) == 1 and ctx.outlet[last]:
                        reached.add(gp[0])
                    break
            if kids:
                ov[s] = kids[0]
            splits[k0] = (s, kids, np.array(fr_) / max(sum(fr_), 1e-9)) if len(kids) > 1 else None
            return bool(kids)

        # main upstream branch of each pixel (the one bringing the most water)
        bp = np.full(ctx.npx, -1)
        by_q = np.argsort(score, kind="stable")
        by_q = by_q[rec0[by_q] >= 0]
        bp[rec0[by_q]] = by_q  # the last (biggest) write wins
        blocked = ctx.BR["blocked"]
        for dl in todo:
            R = dl["R"]
            # (stats: fingers in the region, those with a channel to the sea)
            dl["fingers"] = [0, 0]
            r = np.hypot(ctx.px - dl["x"], ctx.py - dl["y"])
            mouth = ctx.active & (r < R) & ctx.sea[np.maximum(rec0, 0)] & (rec0 >= 0)
            if not mouth.any():
                continue
            # walk up the main river from its mouth to the apex (0.6 R up
            # the river), then on up while it's still the main river; that
            # stretch is pinned so the river can't drift away from the apex
            m0 = np.flatnonzero(mouth)[np.argmax(score[mouth])]
            if score[m0] < 0.2 * dl["q"] / RG.KM2_M_PER_YR_TO_M3S:
                continue
            up, a, run = [m0], -1, 0.0
            while len(up) < 4 * R / ctx.res and bp[up[-1]] >= 0:
                c = bp[up[-1]]
                run += ctx.res * (1.4142 if (c % ctx.nx != up[-1] % ctx.nx and c // ctx.nx != up[-1] // ctx.nx) else 1.0)
                if a < 0 and run > 0.6 * R:
                    a = up[-1]
                if a >= 0 and (score[c] < 0.5 * score[a] or not ctx.active[c]):
                    break
                up.append(c)
            if a < 0 or r[a] > 1.2 * R or assigned[up[up.index(a):]].any():
                continue
            snap = (dict(ov), len(splits), assigned.copy(), blocked.copy())
            trunk = up[up.index(a) + 1:]
            for c in trunk:  # pin the main channel down to the apex
                ov[c] = rec0[c]
            ctx.trunk_px.extend(trunk)
            assigned[[a] + trunk] = True
            blocked[[a] + trunk] = True
            dl["apex"], dl["laid"] = int(a), True
            nb = dl["nb"]  # from the Galloway weights (_deltas): waves leave few mouths, tides many
            if nb < 2:  # a single mouth: no distributaries (the trunk stays pinned)
                continue
            phi = np.arctan2(ctx.py[m0] - ctx.py[a], ctx.px[m0] - ctx.px[a])
            ln = np.hypot(ctx.px[m0] - ctx.px[a], ctx.py[m0] - ctx.py[a])
            cp = np.flatnonzero(coast & ~assigned)
            cd = np.hypot(ctx.px[cp] - ctx.px[a], ctx.py[cp] - ctx.py[a])
            goals = []
            if dl["goals"]:
                # the tips of the fingers (river) or the heads of the funnels
                # (tide): the coast pixel nearest each, not too close to the apex
                lines = dl.get("finger_lines", []) if dl["form"] == "fingers" else []
                for k_, (gx, gy) in enumerate(dl["goals"]):
                    if k_ < len(lines):
                        # a finger's goal is its tip (or its last point in the
                        # region): the branches split towards the tips, far apart;
                        # its own branch enters the finger a tenth of the way out
                        # (they all start from the mouth) and runs out along its axis
                        ln_ = lines[k_]
                        cc_ = np.floor(ln_[:, 0] / ctx.res + ctx.nx / 2).astype(int)
                        rr_ = np.floor(ctx.ny / 2 - ln_[:, 1] / ctx.res).astype(int)
                        ins = np.flatnonzero((cc_ >= 0) & (cc_ < ctx.nx) & (rr_ >= 0) & (rr_ < ctx.ny))
                        j = max(len(ln_) // 10, 1)
                        if len(ins) and ins[-1] > j:
                            q = int(rr_[ins[-1]] * ctx.nx + cc_[ins[-1]])
                            if q not in goals:
                                goals.append(q)
                                via_map[q] = ln_[j:ins[-1] + 1]
                        continue
                    ok = cd > 0.4 * ln
                    if ok.any():
                        q = int(cp[ok][np.argmin(np.hypot(ctx.px[cp[ok]] - gx, ctx.py[cp[ok]] - gy))])
                        if q not in goals:
                            goals.append(q)
            else:
                # coast pixels spread over a fan around the main mouth
                spread = np.radians(min(30.0 + 20.0 * (nb - 1), 130.0))
                ca = (np.arctan2(ctx.py[cp] - ctx.py[a], ctx.px[cp] - ctx.px[a]) - phi + np.pi) % (2 * np.pi) - np.pi
                for th in spread * np.linspace(-0.5, 0.5, nb) + rng.normal(0, 0.05, nb):
                    ok = (np.abs(ca - th) < 0.12) & (cd > 0.5 * ln) & (cd < 2.0 * ln)
                    if ok.any():
                        q = int(cp[ok][np.argmin(cd[ok])])
                        if q not in goals:
                            goals.append(q)
            if len(goals) < 2:
                goals = [int(m0)] + goals
            # order the goals around the fan, so each split divides neighbours
            goals.sort(key=lambda q: (np.arctan2(ctx.py[q] - ctx.py[a], ctx.px[q] - ctx.px[a]) - phi + np.pi) % (2 * np.pi))
            # (the branches stay on low ground: not up into the hills beside the plain)
            top_z[0] = max(float(ctx.base[a]), 0.0) + RG.BRANCH_CLIMB_M  # (no branch onto ground higher than its apex, but a little)
            # (nor across a young volcano held at its cone: the channel rode over it, PW-363)
            blk = blocked | (ctx.target > RG.BRANCH_MAX_Z) | (ctx.vpin > -np.inf)
            grow(a, goals, max(int(0.15 * ln / ctx.res), 2), blk)
            # A finger the split tree's branches didn't reach (the trunk's own
            # course or high ground near the apex in the way) gets a branch of
            # its own from the delta's channel nearest its base, splitting off
            # there with its share of the water: else it was a strip of land
            # with no channel (PW-363).
            sp_src = {sp_[0] for sp_ in splits if sp_ is not None}
            trunk_s = set(trunk)
            for q in goals:
                if q in reached or q not in via_map:
                    continue
                own = np.array([c for c in ov if c not in sp_src and (c in trunk_s or c == a or
                                                                       np.hypot(ctx.px[c] - ctx.px[a], ctx.py[c] - ctx.py[a]) < 1.5 * R)],
                               dtype=np.int64)
                if not len(own):
                    continue
                v0 = via_map[q][0]
                s0 = int(own[np.argmin(np.hypot(ctx.px[own] - v0[0], ctx.py[own] - v0[1]))])
                pix = toward(s0, v0[0], v0[1], ctx.npx, blk, via_map[q], 0)
                snap_k = (dict(ov), assigned.copy())
                first, last, open_ = commit(s0, pix, blk)
                # (out to the sea, or out of the region: a finger running on
                # past its edge, into the halo, ends there)
                ok_ = first >= 0 and ((not open_ and ctx.outlet[last]) or not ctx.region[last])
                if ok_ and open_:  # (an open end mustn't drain back into the delta: a loop)
                    rt = rec0.copy()
                    rt[list(ov)] = list(ov.values())
                    ok_ = len(ZK.receiver_order(rt)) == ctx.npx
                if not ok_:
                    ov.clear()
                    ov.update(snap_k[0])
                    assigned[:] = snap_k[1]
                    continue
                r0 = ov[s0] if s0 in ov else int(rec0[s0])
                share = 1.0 / max(len(goals), 2)
                # (before any split further down its channel: route() divides
                # the water in this order, upstream first)
                down_, c = set(), r0
                while c >= 0 and c not in down_ and len(down_) < ctx.npx:
                    down_.add(c)
                    c = ov[c] if c in ov else int(rec0[c])
                at = next((j for j, sp_ in enumerate(splits) if sp_ is not None and sp_[0] in down_), len(splits))
                splits.insert(at, (s0, [r0, first], np.array([1.0 - share, share])))
                sp_src.add(s0)
                reached.add(q)
            fg = [q for q in goals if q in via_map]
            if 1.6 * dl["wR"] > 0.6:  # (none drawn as land below a river weight of ~0.4)
                dl["fingers"] = [len(fg), sum(q in reached for q in fg)]
            rt = rec0.copy()
            rt[list(ov)] = list(ov.values())
            if len(ZK.receiver_order(rt)) < ctx.npx:  # a branch looped back: no distributaries here
                ov.clear()
                ov.update(snap[0])
                assigned[:], blocked[:] = snap[2], snap[3]
                del splits[snap[1]:]
                dl.pop("apex", None)
                dl["laid"], dl["fingers"][1] = True, 0  # (not tried again)
        return (np.array(list(ov), dtype=np.int64), np.array(list(ov.values()), dtype=np.int64),
                [sp_ for sp_ in splits if sp_ is not None])
    ctx.make_branches = make_branches


def fit_setup(ctx):
    """The slope fit's state: C, the summit softening and cap, the volcano pins.
    Reads: Kr, Pk, S, active, amp_land, cap, carved, cx, cy, fit_log, fit_w, full_px, glacier, lake, land, logC,
    npx, nx, ny, own_s, px, py, res, sel, soft, sp, t_fit, target, vf, vpin, vtarget.
    Writes: cap, fit_c, fit_log, fit_w, logC, rough, soft, t_fit, vpin."""

    # Steady-state stream power: slope = C / K * Q^-m. C (~ the uplift rate
    # over the rock's erodibility) is a smooth field at the coarse cells'
    # scale, fitted so each cell keeps the mean of the target surface as it
    # was before the coarse valleys were cut into it (so the hillslopes
    # between the valleys stand a little higher and each coarse cell keeps
    # its mean: the valleys are cut mass-neutrally, PW-268): fit_c(). A
    # little noise in C varies the relief from valley to valley.
    rad = max(1, int(round(0.3 * ctx.sp / ctx.res)))
    wmask = ctx.land.reshape(ctx.ny, ctx.nx).astype(float)
    ctx.t_fit = np.maximum(np.where(ctx.lake, ctx.target, ctx.target - ctx.carved), 0)
    tmean = box_mean(ctx.t_fit.reshape(ctx.ny, ctx.nx) * wmask, wmask, rad).ravel()
    var = np.exp(0.35 * ZK.fbm(ctx.Pk, 0.25 * ctx.sp, 3, 0.5, ctx.S + 6) / 0.17)
    ctx.logC = np.full(ctx.npx, np.log(30.0))
    ctx.fit_log = []  # (debug: per pass, the cells' summed |mean error| x pixels, and the largest C)
    # summits: slopes taper above `soft`, nothing above `cap`
    ctx.soft = tmean + 0.7 * ctx.amp_land
    ctx.cap = tmean + np.minimum(1.8 * ctx.amp_land, 3000.0)
    ctx.vpin = np.full(ctx.npx, -np.inf)  # young volcanoes: held at their smooth cone
    if ctx.vf is not None:
        tv = np.isfinite(ctx.vtarget)
        ctx.soft = np.where(tv, np.maximum(ctx.soft, ctx.target), ctx.soft)
        ctx.cap = np.where(tv, np.maximum(ctx.cap, ctx.target + 150.0), ctx.cap)
        pin = tv & np.isfinite(ctx.vf["pin"]) & ctx.active
        ctx.cap = np.where(pin, ctx.target + 25.0, ctx.cap)
        ctx.vpin = np.where(pin, ctx.target - 25.0, ctx.vpin)
    ctx.rough = np.where(ctx.glacier, 0.5, 1.0) * var / ctx.Kr

    def fit_c(hh, rec, order, fl, cp):
        """The slope fit's step in log C (PW-298). Per coarse cell, a Newton
        step for h = base + C r: the factor that brings its active land's
        mean to the target's if the relief its own slopes make scaled with C.
        That relief is h above where each pixel's profile starts inside the
        cell (ZK.local_base: where its water leaves the cell, or a held
        point: an outlet, a river's floor, a capped summit, which don't
        respond to C); what lies below that, the cells downstream make, and
        fit for themselves. At most x FIT_STEP or / FIT_STEP a pass, spread
        over the pixels smoothly (FIT_SIGMA of a cell). The old per-pixel
        fit (C *= (box mean of the target / of h)^0.8, on ~20 km boxes)
        took a pixel's whole height above the sea as its own: next to low,
        held river courses it could never reach its box mean, wound up
        (C x1.5 a pass, to ~30,000) and made tributaries' last links walls
        of 400-1000 m; elsewhere it settled 100-200 m off the cell means."""
        held = ZK.local_base(hh, rec, order, ~ctx.active, fl, cp, ctx.own_s)
        dsum = np.bincount(ctx.own_s, np.where(ctx.active, ctx.t_fit - np.maximum(hh, 0), 0.0), minlength=len(ctx.sel))
        rsum = np.bincount(ctx.own_s, np.where(ctx.active & (hh > 0), hh - held, 0.0), minlength=len(ctx.sel))
        cnt = np.bincount(ctx.own_s, ctx.active, minlength=len(ctx.sel))
        ok = (cnt > 0.1 * ctx.full_px) & (rsum > 0)
        step = np.where(ok, np.log(np.clip((rsum + dsum) / np.maximum(rsum, 1e-9), 1 / RG.FIT_STEP, RG.FIT_STEP)), 0.0)
        corr = ZK.weighted_mean(*ctx.fit_w, step, ok.astype(float))
        ctx.fit_log.append((round(float(np.sum(np.abs(dsum[ok])))), round(float(np.exp(ctx.logC[ctx.active].max())), 1)
                        if ctx.active.any() else 0.0))
        return np.nan_to_num(corr)
    ctx.fit_c = fit_c

    ctx.fit_w = ZK.gauss_weights(ctx.px, ctx.py, ctx.cx, ctx.cy, RG.FIT_SIGMA * ctx.sp)


def landscape_loop(ctx):
    """The landscape pass: the stream-power grading iterations, with falls, lakes, distributaries and the slope fit.
    Reads: active, amp_land, bottom, branch, c_idx, course, delta_floor, deltas, edge, fit_c, fjord, glacier,
    glacier_mask, h, hf, idx, iterations, jitter, keep_means, kpix, lake, lake_loss, lake_outlets, lakes, land, lf,
    log, logC, make_branches, npx, nx, ny, outlet, outs, ov_src, place_falls, q_course, rapids, rec, reroute, res,
    rims, ring, ring_px, riv_q, rough, route, sea, soft, srcg, srcq, stages, t0, target, trunk_px, vpin, wD, wR_f,
    zD, z_course.
    Writes: active, c_idx, course, delta_floor, fjord, glacier, h, hf, ice_th, lake_seq, lakes, land, lf_gorges,
    logC, outlet, outs, ov_dst, ov_src, rapids_lift, rec, ring_px, sea, splits, stages."""
    hprev = None
    ctx.course = np.zeros(ctx.npx, bool)  # (the designed falls' courses, once the landscape pass has laid them)
    ctx.c_idx = np.zeros(0, np.int64)
    was_river = ctx.bottom.copy()  # the valley bottom, and every pixel the coarse river's water has run through
    for it in range(ctx.iterations):
        filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
        # (once the network has settled a bit; a delta whose river didn't reach
        # its mouth yet, still finding its way through the region, is tried
        # again on the next iterations, up to two thirds of the way)
        todo = [dl for dl in ctx.deltas if not dl.get("laid")] if ctx.iterations // 3 <= it <= 2 * ctx.iterations // 3 else []
        if todo:
            ctx.ov_src, ctx.ov_dst, ctx.splits = ctx.make_branches(ctx.rec, order, todo)
            ctx.branch[:] = False
            ctx.branch[ctx.ov_src] = True
            ctx.branch[np.asarray(ctx.trunk_px, dtype=np.int64)] = False
            # levees: the land along the distributaries stands a little
            # above the plain, more so on a river-dominated delta
            chan = np.zeros(ctx.npx, bool)
            chan[ctx.ov_src] = True
            lev = RG._dilate(chan.reshape(ctx.ny, ctx.nx), 1).ravel() & ~chan & ctx.active & (ctx.wD > 0.3)
            ctx.delta_floor = np.where(lev, np.maximum(ctx.delta_floor, ctx.zD + 0.5 + 3.0 * ctx.wR_f), ctx.delta_floor)
        ctx.rec, order, split_ok = ctx.reroute(ctx.rec, order)
        ctx.outs = ctx.lake_outlets(ctx.rec)
        Q, _ = ctx.route(ctx.srcq, ctx.rec, order, ctx.outs, split_ok, ctx.lake_loss)
        Qg, _ = ctx.route(ctx.srcg, ctx.rec, order, ctx.outs, split_ok)
        diag = (ctx.rec >= 0) & ((ctx.rec % ctx.nx) != (ctx.idx % ctx.nx)) & ((ctx.rec // ctx.nx) != (ctx.idx // ctx.nx))
        dist = ctx.res * np.where(diag, 1.4142, 1.0)
        # coarse river courses count as carrying at least their coarse discharge
        slope = np.minimum(np.exp(ctx.logC) * ctx.rough * np.maximum(np.maximum(Qg, ctx.riv_q), 1e-3) ** -RG.SPL_M, RG.MAX_SLOPE)
        ctx.c_idx, c_val, step, flg, cliff, _, (b_idx, b_val) = ctx.place_falls(ctx.rec, Q, hprev)
        fl, cp = ctx.rims(ctx.rec, ctx.outs, step)
        was_river |= Q >= 0.3 * ctx.q_course
        # (on a reach with falls, only in the valley bottom: a stream wandering
        # off the course isn't held up at the plateau's level)
        flc = np.where(was_river & ((ctx.kpix < 0) | ctx.bottom), ctx.z_course, -np.inf)
        # (nor a delta's distributaries above the land beside them: held at the
        # coarse river's valley floor, or a falls reach's foot, they ran 30-90 m
        # above the plain the landscape pass grades beside them, PW-363)
        if hprev is not None and ctx.branch.any():
            g_ = np.where(ctx.active & ~ctx.branch & (Q * RG.KM2_M_PER_YR_TO_M3S < 30.0), hprev, np.inf).reshape(ctx.ny, ctx.nx)
            lo_ = g_.copy()
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    lo_ = np.minimum(lo_, RG._shift(g_, dr, dc, np.inf))
            flc[ctx.branch] = np.minimum(flc[ctx.branch], lo_.ravel()[ctx.branch] + 0.5)
        flc[ctx.c_idx] = c_val  # the river itself, on reaches with falls
        cp[ctx.c_idx] = np.minimum(cp[ctx.c_idx], c_val + 1.0)  # ... at its staircase, not above it
        np.minimum.at(cp, b_idx, b_val + 1.0)
        # (beach ridges and levees, but not under the channels themselves)
        fl = np.maximum(np.maximum(np.maximum(np.maximum(fl, flg), flc), ctx.vpin),
                        np.where(Q * RG.KM2_M_PER_YR_TO_M3S < 30.0, ctx.delta_floor, -np.inf))
        ctx.h = ctx.target.copy()
        ZK.integrate(ctx.h, ctx.rec, order, slope, dist, ~ctx.active, fl, ctx.soft, 0.5 * ctx.amp_land + 1, cp)
        hprev = ctx.h
        if it < ctx.iterations - 1:
            ctx.logC = ctx.logC + ctx.fit_c(ctx.h, ctx.rec, order, fl, cp)
    ctx.glacier, ctx.ice_th = ctx.glacier_mask(ctx.h, ctx.sea | ctx.lake)  # on the finished valleys
    ctx.stages = {"landscape": ctx.h.copy()}  # (debug: the height after each stage, PW-125's diagnostic)
    # soften D8 streaks and knife-edge ridges on hillslopes; keep channels sharp
    # (a channel from the drainage of 50 px, but on pixels coarser than
    # KD_RES_KM from the area that is at KD_RES_KM, as creep's diffusivity:
    # else a 20-50 m^3/s stream on 4 km pixels was no channel and creep
    # lifted its bed, PW-125)
    rch = min(ctx.res, RG.KD_RES_KM)
    chan = np.clip(np.log10(np.maximum(Qg, 1e-3) / (50 * rch * rch)) / 2, 0, 1)
    cliff = RG._dilate(cliff.reshape(ctx.ny, ctx.nx), 2).ravel()  # falls, gorges and their walls don't creep
    kd = RG.creep_kd(ctx.res) * np.where(ctx.active & ~cliff, np.where(ctx.glacier, RG.KD_ICE, RG.KD * (1 - 0.8 * chan)), 0.0)
    # (creep rounds the hillslopes, but never lifts a stream's bed: in a deep
    # valley it would fill the channel towards its walls in places, leaving
    # steps and pits along the stream, undesigned 'falls'. Under ice it does,
    # the ice surface is smooth, but by no more than ICE_SNOUT_GRAD m per km
    # in from the ice's edge: else the glacier ends in a cliff.)
    stream = ctx.active & (chan > 0)
    lift = np.where(ctx.glacier, RG.ICE_SNOUT_GRAD * ctx.res * ZK.inside_distance(ctx.glacier, ctx.nx, ctx.ny, False), 0.0)
    h0 = ctx.h
    for _ in range(RG.SMOOTH_STEPS):
        hd = ZK.diffuse(ctx.h, kd, ctx.active, ctx.nx, ctx.ny)
        ctx.h = np.where(stream, np.minimum(hd, np.maximum(ctx.h, h0 + lift)), hd)
    # (what creep moves off the hillslopes and the streams don't take up, and
    # what leaks into the sea at the coast, is put back on the hillslopes:
    # each cell keeps its mean, PW-268)
    ctx.h = ctx.keep_means(ctx.h, h0, ctx.active & ~stream)
    ctx.stages["creep"] = ctx.h.copy()
    solid = np.zeros(ctx.npx, bool)  # (a shield's domes: not cut through, nor capped)
    if ctx.lf is not None:
        # Landform bedding (zoom.landforms): benches, scarps and cliffs of the
        # finished landscape, each coarse cell's mean kept. Not on glaciers,
        # lake rims and outflows, nor the courses of designed falls and their
        # banks (their staircase is the river's; the remap would add steps to
        # it or flatten its falls).
        ctx.course = np.zeros(ctx.npx, bool)
        ctx.course[ctx.c_idx] = True
        dco = ZK.inside_distance(~ctx.course, ctx.nx, ctx.ny, False) * ctx.res
        wk = max(RG.BANK_KM, 2 * ctx.res)
        where = ctx.active & ~ctx.glacier & ~ctx.ring & ~ctx.rapids
        # (on the drainage of the crept surface; channels: >= LF_CHANNEL_Q)
        ctx.hf, rec_, order_ = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
        ctx.hf = np.where(ctx.active, np.maximum(ctx.h, ctx.hf), ctx.h)
        chan_ = (Qg * RG.KM2_M_PER_YR_TO_M3S >= RG.LF_CHANNEL_Q) | ~ctx.active
        q_ = accumulate(rec_, order_, ctx.srcq) * RG.KM2_M_PER_YR_TO_M3S  # (m^3/s along this drainage)
        mask_ = where * smoothstep(wk + ctx.res, wk + 4 * ctx.res, dco)
        # (cut only inside the classes' reach: a sill where a river leaves it
        # would otherwise be cut far down its course; and not across the
        # closed basins of a rift or a scoured shield, but for the big rivers
        # crossing them: those depressions are filled flat or hold lakes)
        fixed_ = ((mask_ <= 0) & ~(ctx.edge & ctx.land)) | (ctx.lf.weight() < 0.02)
        # (the shape hooks' structures die out over a few km towards those courses: a water gap)
        mask_s = where * smoothstep(wk + ctx.res, wk + max(4 * ctx.res, 5.0), dco)
        hr = ctx.lf.remap(ctx.hf, mask_, rec_, order_, chan_, mask_s, q_)
        # (after the remap: the glacial class's basins, overdeepened troughs and moraine dams, come from it)
        keep_ = fixed_ | ((ctx.lf.basins() > 0.5) & (q_ < RG.BASIN_THROUGH_Q) & ctx.active)
        # (solid rock the remap raised, a shield's domes, isn't cut through:
        # the flow paths across it pond and spill round it, PW-168)
        solid = ctx.lf.solid() > 0.5
        keep_ = keep_ | solid
        # (each cell's mean restored on its hillslopes, as after creep: a
        # correction on the channels too lifted a stream's bed where the
        # classes weigh much over its foot where they weigh little, a step
        # of 100-600 m in the stream, PW-125)
        hc_ = ZL.cut(hr, rec_, order_, keep_, ctx.nx, ctx.ny, ctx.res, fixed_)
        ctx.h = ctx.keep_means(hc_, ctx.h, ctx.active, np.clip(3 * ctx.lf.weight(), 0, 1) * ~chan_)
        ctx.stages["landform_mean_correction"], ctx.stages["landform_channels"] = ctx.h - hc_, chan_
        # (a sill the remap, the correction or the summits' caps leave across a
        # flow path is cut through rather than filled into a lake; the region's
        # edge, an outlet held at the target, is lowered too where land drains into it)
        # falls over the classes' cliffs retreat into gorges (PW-150)
        ctx.h, ctx.lf_gorges = ZL.scarp_gorges(ctx.h, rec_, q_, ctx.lf.weight(), ctx.nx, ctx.ny, ctx.res, fixed_ | ~ctx.active)
        # (the summits' cap is the landscape pass's: a shield's domes stand above it, PW-168)
        ctx.h = ZL.cut(np.where(ctx.active & ~solid, np.minimum(ctx.h, cp), ctx.h), rec_, order_, keep_, ctx.nx, ctx.ny, ctx.res, fixed_)
    ctx.stages["landform"] = ctx.h.copy()
    # fjords: a glacial trough carved below the sea that joins it is flooded (zoom.glacial); it is sea from here on
    ctx.fjord = np.zeros(ctx.npx, bool)
    if ctx.lf is not None:
        ctx.fjord = ctx.lf.drown(ctx.h, ctx.sea) & ctx.active
        if ctx.fjord.any():
            ctx.land, ctx.sea = ctx.land & ~ctx.fjord, ctx.sea | ctx.fjord
            ctx.active, ctx.outlet = ctx.active & ~ctx.fjord, ctx.outlet | ctx.fjord
    ctx.h = np.where(ctx.active, np.maximum(ctx.h, 0.5), ctx.h)  # creep mustn't pull the coast below the sea
    if ctx.lakes:
        _, rec_s, order_s = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
        q_s = accumulate(rec_s, order_s, ctx.srcq) * RG.KM2_M_PER_YR_TO_M3S
        ctx.h, shore_px = RG.shore_apron(ctx.h, ctx.lake, ctx.lakes, ctx.active & ~ctx.glacier & ~solid, ctx.ring | ctx.rapids, ctx.c_idx,
                                  rec_s, order_s, q_s, ctx.nx, ctx.ny, ctx.res)
        if shore_px:
            ctx.log(f"  {shore_px} px of lake shore graded up from the water (PW-531)")
    h_pre = ctx.h
    ctx.h = np.where(ctx.ring | ctx.rapids, np.maximum(ctx.h, fl), ctx.h)  # nor the rims below their lake, nor its outflow's rapids
    ctx.h = np.where(ctx.active & ~solid, np.minimum(ctx.h, cp), ctx.h)  # nor lift a lake's outflow above the lake
    ctx.rapids_lift = np.where(ctx.rapids & ~ctx.glacier, np.maximum(ctx.h - h_pre, 0.0), 0.0)  # (debug: how far the rapids hold the ground up)
    ctx.log(f"  landscape pass: {ctx.iterations} iterations [{time.time() - ctx.t0:.1f}s]")

    # A lake fragment that should pass its water on but found no way out
    # (all of its shore drains back into it) would swallow its rivers: it
    # becomes land instead, a flat at its level that the rivers cross.
    ctx.rec = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)[1]
    ctx.outs = ctx.lake_outlets(ctx.reroute(ctx.rec, ZK.receiver_order(ctx.rec))[0])
    sink = [j for j, lk in enumerate(ctx.lakes) if lk["exit"] is not None and ctx.outs[j] < 0
            and not (ctx.match and ctx.m_pin[lk["px"]].mean() > 0.5)]  # (a neighbour's lake on held ground: its outlet is the neighbour's)
    if sink:
        for j in sink:
            ctx.lake[ctx.lakes[j]["px"]] = False
        kept = [j for j in range(len(ctx.lakes)) if j not in sink]
        ctx.lakes, ctx.ring_px = [ctx.lakes[j] for j in kept], [ctx.ring_px[j] for j in kept]
        ctx.lake_seq = sorted(range(len(ctx.lakes)), key=lambda j: -ctx.lakes[j]["level"])
        ctx.outlet = ctx.sea | ctx.edge | ctx.lake
        ctx.active = ctx.land & ~ctx.edge & ~ctx.lake
        ctx.log(f"  {len(sink)} lake fragments without an outlet made land")


def final_drainage(ctx):
    """The final drainage, carved falls, lake fix-ups, glaciers redrawn on the finished valleys and the rivers'
    discharge.
    Reads: S, active, bi_island, c_idx, course, depth, discharge, fr, g, glacier, h, halo, idx, isl, jitter, kps,
    lake, lake_depth, lake_loss, lake_outlets, lakes, land, lf, lf_gorges, lf_lake, lf_sink, log, n_in, npx, nx, ny,
    outlet, outs, place_falls, plunge, px, py, rapids, rec, region, reroute, res, ring, route, sea, srcq, surf,
    top_falls.
    Writes: active, all_falls, area, discharge, g, h, lake_depth, lake_in, lf_counts, lf_lake, lf_overlay, lf_sink,
    outlet, outs, plunge, rec, top_falls."""
    # --- final drainage --------------------------------------------------
    if ctx.match:  # (the ramp blended to the neighbours' heights first, PW-1301)
        from . import match as ZM
        ZM.blend(ctx)
    filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
    # tall drops become carved falls: tiers, a gorge retreated up into the plateau, walls round the lip
    # and a funnel round the foot (zoom.falls, PW-517); the drainage is found again on the carved ground
    ctx.h, falls_carved, tier_pools = ZFL.carve(ctx.h, filled, ctx.rec, order, ctx.active & ~ctx.glacier, ctx.srcq * RG.KM2_M_PER_YR_TO_M3S, ctx.nx, ctx.ny, ctx.res, ctx.S)
    if falls_carved:
        filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
        ctx.log(f"  {len(falls_carved)} tall falls carved (tiers, gorge, walls): "
            + ", ".join(f"{f['drop_m']:.0f} m in {f['tiers']}" for f in falls_carved[:4]))
    # a landform's closed depressions (a rift's basins, a scoured shield's
    # rock basins) hold water where the class lets them (Synth.lakes) and
    # their water balance says (zoom.landforms.basin_lakes, PW-167): a lake
    # to the brim where their inflow beats the evaporation (smaller ones
    # spilling into the next), else a closed lake below the spill or a dry
    # flat where the streams end; the rest are filled flat
    ctx.lf_lake, lf_depth, ctx.lf_sink, ctx.lf_counts = np.zeros(ctx.npx, bool), np.zeros(ctx.npx), np.zeros(ctx.npx, bool), {}
    h_pre_fill = ctx.h.copy()
    if ctx.lf is not None:
        surf_b, ctx.lf_lake, lf_depth, ctx.lf_sink, ctx.lf_counts = ZL.basin_lakes(
            ctx.h, filled, ctx.rec, order, ctx.active & ~ctx.glacier, ctx.lf.lakes(), ctx.srcq, ctx.lake_loss, ctx.res, ctx.nx, ctx.ny,
            RG.LF_LAKE_M, RG.LF_LAKE_KM2, RG.LF_FULL_KM2, count=ctx.region)
        ctx.h = np.where(ctx.active, surf_b, ctx.h)
        if ctx.lf_sink.any():  # (closed lakes and dry basins: their streams end there)
            ctx.outlet = ctx.outlet | ctx.lf_sink
            ctx.active = ctx.active & ~ctx.lf_sink
            filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
    ctx.h = np.where(ctx.active, np.maximum(ctx.h, filled), ctx.h)  # no pits left: everything drains
    filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
    # the flats that filling left are not land: a basin on high ground is a valley floor falling to its
    # exit (alluvial fill), the outlet cut into its rim (PW-521)
    flats = ctx.active & ~ctx.lf_lake & ~ctx.lf_sink & (ctx.h - h_pre_fill > 0.2) & (ctx.h > RG.FLOOR_MIN_M)
    protect = ctx.ring | ctx.rapids | ctx.course
    protect[ctx.c_idx] = True
    protect = RG._dilate(protect.reshape(ctx.ny, ctx.nx), 4).ravel()
    if flats.any():
        ctx.h, g_px, g_cut = ZK.grade_fills(ctx.h, h_pre_fill, flats, ctx.rec, order, ctx.outlet, ctx.active, protect, ctx.nx, ctx.res, RG.FLOOR_SLOPE, RG.FLOOR_MAX_SHARE)
        ctx.log(f"  {int(flats.sum())} px of filled flats graded to valley floors ({RG.FLOOR_SLOPE:g} m/km), {int(g_cut.sum())} px of outlet notch")
        filled, ctx.rec, order = ZK.flood_d8(ctx.h, ctx.outlet, ctx.nx, ctx.ny, 1e-3, ctx.jitter)
    rec0 = ctx.rec
    ctx.rec, order, split_ok = ctx.reroute(ctx.rec, order)
    # The pinned courses (reaches with falls, delta trunks and distributaries)
    # were laid out on an earlier surface: where one now runs uphill, a small
    # step (<= SETTLE_M) is evened out by lifting the pixel above it; at a big
    # one (a course the water has left) the course is unpinned.
    up = (ctx.rec != rec0) & (ctx.rec >= 0) & ctx.active
    up &= ctx.h[np.maximum(ctx.rec, 0)] > ctx.h + RG.SETTLE_M
    if up.any():
        r2 = np.where(up, rec0, ctx.rec)
        o2 = ZK.receiver_order(r2)
        if len(o2) == ctx.npx:
            ctx.rec, order = r2, o2
    diag = (ctx.rec >= 0) & ((ctx.rec % ctx.nx) != (ctx.idx % ctx.nx)) & ((ctx.rec // ctx.nx) != (ctx.idx // ctx.nx))
    ZK.settle(ctx.h, ctx.rec, order, ~ctx.active, ctx.res * np.where(diag, 1.4142, 1.0), RG.SETTLE_M)
    ctx.outs = ctx.lake_outlets(ctx.rec)
    Q, ctx.lake_in = ctx.route(ctx.srcq, ctx.rec, order, ctx.outs, split_ok, ctx.lake_loss)
    ctx.area, _ = ctx.route(np.full(ctx.npx, ctx.res * ctx.res), ctx.rec, order, ctx.outs, split_ok, water=False)
    ctx.discharge = np.where(ctx.land, Q * RG.KM2_M_PER_YR_TO_M3S, 0.0)
    ws_f = np.where(ctx.lake, ctx.surf, np.where(ctx.sea, 0.0, ctx.h))
    # the designed falls: where they ended up, and a plunge pool at each foot
    lips = ctx.place_falls(ctx.rec, Q, ctx.h)[5]
    # every fall at least WF_MIN_DROP high (a few pixels apart)
    falls = RG.waterfalls(ws_f, np.where(ctx.glacier, 0.0, ctx.discharge), ctx.rec, ctx.nx, ctx.ny, ctx.res,  # (no falls under the ice)
                       {int(o): ctx.lakes[j]["level"] for j, o in enumerate(ctx.outs) if o >= 0},
                       designed=[lp for lp, _, _ in lips], top=None, sep_km=0.0)
    pool = np.zeros(ctx.npx)
    for p_, d_ in tier_pools:  # (the basins below the carved falls' tiers)
        if ctx.active[p_]:
            pool[p_] = max(pool[p_], d_)
    for lip, st, kp in lips:
        foot = int(ctx.rec[lip])
        hgt = float(ws_f[lip] - ws_f[foot])
        st["lip_px"], st["height_m"] = list(divmod(lip, ctx.nx)), round(hgt, 1)
        if hgt < RG.KP_MIN_STEP or not ctx.active[foot]:
            continue
        # the listed fall over this lip, if any: the pool goes at its foot,
        # where its drop ends (below most of a fall over several pixels, PW-341)
        r0, c0 = divmod(lip, ctx.nx)
        f = next((f for f in falls if max(abs(f["px"][0] - r0), abs(f["px"][1] - c0)) <= 3 and "kind" not in f),
                 None)
        if f is not None and ctx.active[f["_foot"]]:
            foot, hgt = f["_foot"], max(hgt, f["height_m"])
        # plunge pools are roughly as deep as the fall is high, up to ~60 m (Niagara ~50 m below a 51 m fall)
        pool[foot] = max(pool[foot], float(np.clip(0.6 * hgt, 3.0, 60.0)))
        if f is not None:
            f.update({"kind": "lip", "gorge_km": round(float(st["gorge_km"]), 1),
                      "lip_resistance": round(kp["resistance"], 2),
                      "coarse_reach_drop_m": round(kp["excess_m"] + RG.KP_GRADED * kp["reach_km"]),
                      "coarse_reach_km": round(kp["reach_km"]), "plunge_pool_m": round(float(pool[foot]), 1),
                      "_kp": ctx.kps.index(kp)})
    # falls over a landform's cliffs (a scarp, a bench, a fault scarp): their
    # own kind, and a plunge pool at the foot
    dom = ctx.lf.dominant() if ctx.lf is not None else np.zeros(ctx.npx, int)
    for f in falls:
        if f["from_lake"]:
            f.setdefault("kind", "lake outlet")
        k = int(dom[f["px"][0] * ctx.nx + f["px"][1]])
        if "kind" in f or k not in RG.LF_FALL_KIND:
            continue
        f["kind"], f["landform"] = RG.LF_FALL_KIND[k], ZL.LF.CLASSES[k][1]
        # (its gorge, if it retreated into one: the fall at the gorge's head)
        ctx.g = [km for p, km in ctx.lf_gorges if max(abs(p // ctx.nx - f["px"][0]), abs(p % ctx.nx - f["px"][1])) <= 3]
        f["gorge_km"] = round(max(ctx.g), 1) if ctx.g else 0.0
        foot = f["_foot"]
        if foot >= 0 and ctx.active[foot] and not ctx.lf_lake[foot]:
            pool[foot] = max(pool[foot], float(np.clip(0.6 * f["height_m"], 3.0, 60.0)))
            f["plunge_pool_m"] = round(float(pool[foot]), 1)
    for f in falls:
        f.setdefault("kind", "drop")
        f.pop("_foot", None)
        k = f["px"][0] * ctx.nx + f["px"][1]
        f["lat"], f["lon"] = (round(v, 3) for v in RG._latlon(ctx.fr.to_sphere(ctx.px[[k]], ctx.py[[k]])[0]))
    falls = [f for f in falls if ctx.halo <= min(f["px"]) and max(f["px"]) < ctx.halo + ctx.n_in]  # (not in the halo)
    # the panel's summary: the biggest by power, ~15 km apart, each with its
    # reach's other falls (cascades), which the spacing leaves off it
    ctx.top_falls, sep = [], max(6, int(round(15 / ctx.res)))
    for f in falls:
        if len(ctx.top_falls) >= 5:
            break
        if any(max(abs(f["px"][0] - t["px"][0]), abs(f["px"][1] - t["px"][1])) < sep for t in ctx.top_falls):
            continue
        ctx.top_falls.append(dict(f))
    for f in falls + ctx.top_falls:
        if "_kp" in f:
            f["cascades"] = [{"px": st["lip_px"], "height_m": st["height_m"]} for st in ctx.kps[f.pop("_kp")]["steps"]
                             if "lip_px" in st and st["height_m"] >= RG.KP_MIN_STEP
                             and max(abs(st["lip_px"][0] - f["px"][0]), abs(st["lip_px"][1] - f["px"][1])) > 3]
    # the tiers the carve gave the run a fall belongs to (a finer zoom splits the fall's drop the same way)
    for f in falls + ctx.top_falls:
        near = [c for c in falls_carved if max(abs(c["px"][0] - f["px"][0]), abs(c["px"][1] - f["px"][1])) <= max(4, int(8 / ctx.res))]
        if near:
            c = min(near, key=lambda c: max(abs(c["px"][0] - f["px"][0]), abs(c["px"][1] - f["px"][1])))
            f["tiers_m"] = c["tier_m"]
    # every listed fall with what the viewer's card shows (zoom.html's Waterfalls overlay)
    card = ("px", "lat", "lon", "height_m", "discharge_m3s", "kind", "length_km", "from_lake", "gorge_km",
            "plunge_pool_m", "landform", "lip_resistance", "cascades", "tiers_m")
    ctx.all_falls = sorted(({k: f[k] for k in card if k in f} for f in falls), key=lambda f: -f["height_m"])
    ctx.h = np.where(ctx.lake, ctx.surf - ctx.depth, ctx.h)
    ctx.lake_depth = np.where(ctx.lake, ctx.depth, 0.0)
    ctx.h = np.where(ctx.lf_lake, ctx.h - lf_depth, ctx.h)  # (landform lakes: their beds)
    ctx.lake_depth = np.where(ctx.lf_lake, lf_depth, ctx.lake_depth)
    # plunge pools: small lakes at the foot of the falls (the water stays at the river's level)
    ctx.plunge = pool > 0
    ctx.h = np.where(ctx.plunge, ctx.h - pool, ctx.h)
    ctx.lake_depth = np.where(ctx.plunge, pool, ctx.lake_depth)
    # landform overlays on the finished land (zoom.landforms: Landforms.finish):
    # dunes, karst's dolines, towers and poljes (ponds where they reach the
    # water table), karst streams sinking (dry valleys) and resurging
    ctx.lf_overlay = {}
    if ctx.lf is not None:
        fz = ctx.lf.finish(ctx.h, {"rec": ctx.rec, "order": order, "q": ctx.discharge, "water": ctx.sea | ctx.lake | ctx.lf_lake | ctx.plunge,
                           "ice": ctx.glacier, "active": ctx.active})
        ctx.h, ctx.discharge, ctx.lf_overlay = fz["h"], np.where(ctx.land, fz["q"], 0.0), fz["stats"]
        ctx.lf_lake = ctx.lf_lake | fz["pond"]
        ctx.lake_depth = np.where(fz["pond"], fz["pond_depth"], ctx.lake_depth)
    if ctx.bi_island.any():  # (the barrier islands stand 1.5-3 m: the mean correction and the landscape pass had lifted them)
        ctx.h = np.where(ctx.bi_island, ZC.ISLAND_M * (0.5 + 0.5 * ctx.isl["u"]), ctx.h)


def shoreface(ctx):
    """The shoreface: the sea floor shoals to the shore along Dean's profile, each cell's mean kept.
    Reads: area, depth, discharge, h, keep_means, lake_in, lake_loss, lakes, land, nx, ny, outs, res, sea, surf_f,
    vf, wave_f, wv.
    Writes: area, h, lake_info."""
    # --- shoreface (zoom.coastal, PW-327): the sea floor shoals to the shore
    # along Dean's profile, then the inner shelf, where the shore isn't rocky;
    # each cell's mean kept by deepening the sea floor further out
    if ctx.sea.any():
        rocky = ZCL.rocky_shore(ctx.h, ctx.land, ctx.surf_f, ctx.nx, ctx.ny, ctx.res)
        hs_, reach = ZCL.shoreface(ctx.h, ctx.sea, rocky, ctx.wave_f, ctx.nx, ctx.ny, ctx.res, ctx.wv if ctx.vf is not None else None)
        ctx.h = ctx.keep_means(hs_, ctx.h, ctx.sea, 1 - reach)
        ctx.h = np.where(ctx.sea, np.minimum(ctx.h, -0.5), ctx.h)
    ctx.area = np.where(ctx.land, ctx.area, 0.0)
    ctx.lake_info = sorted(({"area_km2": round(len(lk["px"]) * ctx.res * ctx.res), "level_m": round(lk["level"], 1),
                         "mean_depth_m": round(float(ctx.depth[lk["px"]].mean()), 1),
                         "max_depth_m": round(float(ctx.depth[lk["px"]].max()), 1),
                         "inflow_m3s": round(float(ctx.lake_in[j] * RG.KM2_M_PER_YR_TO_M3S), 1),
                         "evaporation_m3s": round(float(ctx.lake_loss[lk["px"]].sum() * ctx.res * ctx.res * RG.KM2_M_PER_YR_TO_M3S), 1),
                         "outlet": [int(ctx.outs[j] // ctx.nx), int(ctx.outs[j] % ctx.nx)] if ctx.outs[j] >= 0 else None,
                         # (how fast its outflow's rapids step down: outflow_grad, PW-123)
                         "outflow_grad_m_km": round(lk["grad"], 1) if ctx.outs[j] >= 0 else None,
                         "outflow_m3s": round(float(ctx.discharge[ctx.outs[j]]), 1) if ctx.outs[j] >= 0 else 0.0}
                        for j, lk in enumerate(ctx.lakes)), key=lambda d: -d["area_km2"])
