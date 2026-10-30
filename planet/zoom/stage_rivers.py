"""The regional zoom build's coarse rivers (carved into the target surface as valleys, with their waterfalls and the
inflow from outside the region) and the categorical layers (rock, climate, landform) taken from the nearest coarse cell.

Each stage takes the build's context (`ctx`, see regional.ZoomCtx), reads what the stages before it left on it,
and leaves its own results on it. A stage's docstring lists the context names it reads and writes. The helpers and
constants shared with the rest of the zoom are regional's (`RG.`).
"""
from __future__ import annotations

import time

import numpy as np

from ..geo import R_KM, arc_km
from . import kernels as ZK
from . import regional as RG
from ..geo import smoothstep


def coarse_rivers(ctx):
    """The coarse rivers carved in as valleys (with knickpoints and staircases for falls) and the inflow from outside.
    Reads: L, S, cell_area, cexit, clab, clamp, clvl, cqout, cut, deltas, down, elev, flow, fr, g, ground_up, h,
    inflow, inflow_pts, inside, kpix, kps, lake_c, land, log, n_rivers_in, npx, nx, ny, pin_pairs, px, py, r_c, res,
    riv_ids, river_min_flow, river_segs, rock, s_pix, scarp, sel, size_in, size_km, sp, t0, wD, xs, ys, zD,
    z_course.
    Writes: bottom, carved, cexit, cgrad, clab, clvl, cqout, cut, h, inflow, inflow_pts, inside, kpix, kps, lake_c,
    n_rivers_in, pin_pairs, q_course, riv_ids, riv_q, river_segs, s_pix, z_course."""
    # --- coarse rivers -> valleys + inflow --------------------------------
    coast_cap = RG.COAST_FLOOR_GRAD * ctx.res * ZK.inside_distance(ctx.land, ctx.nx, ctx.ny, False)  # (see z_course)
    # (on a delta plain, no higher than the plain: a coarse river's floor
    # held above it, a falls reach's foot included, raised its distributaries
    # 30-90 m above the plain beside them, PW-363)
    coast_cap = np.where(ctx.wD > 0, (1 - ctx.wD) * coast_cap + ctx.wD * np.minimum(coast_cap, ctx.zD), coast_cap)
    ctx.clab, ctx.clvl, ctx.cexit = RG.coarse_lakes(ctx.g, ctx.L, ctx.elev)
    # each coarse lake's outflow in the world (what its lake cells pass to
    # its exit, km^2 m/yr as the inflows): the zoom sees only the part of a
    # big lake's catchment inside it (PW-060)
    ctx.cqout = np.zeros(len(ctx.clvl))
    for k_, e_ in enumerate(ctx.cexit):
        if e_ >= 0:
            cc_ = np.flatnonzero((ctx.clab == k_) & (ctx.down == e_))
            ctx.cqout[k_] = float(ctx.flow[cc_].max()) * ctx.cell_area if len(cc_) else 0.0
    ctx.cgrad = RG.outflow_grad(ctx.g, ctx.elev, ctx.down, ctx.clab, ctx.clvl, ctx.cexit, 2 * ctx.sp)  # (the rapids below each lake: rims())
    ctx.lake_c = ctx.clab >= 0
    in_sel = np.zeros(ctx.g.n, bool)
    in_sel[ctx.sel] = True
    riv = in_sel & (ctx.elev > 0) & (ctx.flow >= ctx.river_min_flow) & (ctx.down >= 0)
    ctx.riv_ids = np.flatnonzero(riv)
    ctx.inflow = np.zeros(ctx.npx)
    T = np.full(ctx.npx, np.inf)
    ctx.z_course, ctx.q_course = np.full(ctx.npx, -np.inf), np.full(ctx.npx, np.inf)
    ctx.kpix, ctx.s_pix, ctx.bottom = np.full(ctx.npx, -1), np.zeros(ctx.npx), np.zeros(ctx.npx, bool)  # reach with falls (index into kps) and arc length, per pixel
    ctx.riv_q = np.zeros(ctx.npx)  # coarse discharge along the coarse river courses
    ctx.carved = np.zeros(ctx.npx)  # how far the coarse rivers' valleys cut the surface down (<= 0)
    ctx.n_rivers_in = 0  # (into the region, PW-340; the inflow itself comes in at the built area's edge)
    ctx.river_segs = []
    polys, ctx.inflow_pts = {}, []  # warped coarse river polylines per cell; (pixel, radius px) where rivers enter
    ctx.pin_pairs = []  # (pixel, receiver) along the courses of reaches with falls
    ctx.kps = []
    if len(ctx.riv_ids):
        up_main = {}
        for i in ctx.riv_ids:  # main upstream branch of each river cell
            d = ctx.down[i]
            if riv[d] and (d not in up_main or ctx.flow[i] > ctx.flow[up_main[d]]):
                up_main[d] = i
        # valley floor per river cell, monotone downstream (Kahn order)
        indeg = {i: 0 for i in ctx.riv_ids}
        for i in ctx.riv_ids:
            if riv[ctx.down[i]]:
                indeg[ctx.down[i]] += 1
        r_cell = np.zeros(ctx.g.n)
        r_cell[ctx.sel] = ctx.r_c
        zfl = {}
        queue = [i for i in ctx.riv_ids if indeg[i] == 0]
        while queue:
            i = queue.pop()
            e = ctx.elev[i]
            z = e - e * (0.12 + 0.33 * r_cell[i])
            zfl[i] = min(z, zfl.get(i, np.inf))
            d = ctx.down[i]
            if riv[d]:
                zfl[d] = min(zfl.get(d, np.inf), zfl[i])
                indeg[d] -= 1
                if indeg[d] == 0:
                    queue.append(d)
        cxy = {}

        def xy(i):
            if i not in cxy:
                a, b = ctx.fr.to_plane(ctx.g.centers[i][None])
                cxy[i] = np.array([a[0], b[0]])
            return cxy[i]

        segs = []
        for i in ctx.riv_ids:
            d = ctx.down[i]
            p1, p2 = xy(i), xy(d)
            p0 = xy(up_main[i]) if i in up_main else 2 * p1 - p2
            dd = ctx.down[d]
            p3 = xy(dd) if (riv[d] and dd >= 0) else 2 * p2 - p1
            pts = RG._catmull_rom(p0, p1, p2, p3, 12)
            z1 = zfl[i]
            z2 = zfl[d] if riv[d] else (min(ctx.elev[d], z1) if ctx.lake_c[d] or ctx.elev[d] > 0 else 0.0)
            z2 = min(z2, z1)
            q = ctx.flow[i] * ctx.cell_area  # km^2 m/yr
            segs.append((pts, z1, z2, q, r_cell[i], i))
        # warp the polylines with a smooth vector noise field (meanders)
        allp = np.concatenate([s[0] for s in segs])
        sp_pts = np.ascontiguousarray(ctx.fr.to_sphere(allp[:, 0], allp[:, 1]) * R_KM)
        lw = 0.6 * ctx.sp
        wamp = 0.10 * ctx.sp / 0.17
        wx = ZK.fbm(sp_pts, lw, 4, 0.5, ctx.S + 11) * wamp
        wy = ZK.fbm(sp_pts, lw, 4, 0.5, ctx.S + 12) * wamp
        # (no meanders near a delta's mouth: the river must arrive at its delta)
        for dl in ctx.deltas:
            dd = np.hypot(allp[:, 0] - dl["x"], allp[:, 1] - dl["y"])
            damp = smoothstep(0.3 * dl["R"], 1.5 * dl["R"], dd)
            wx, wy = wx * damp, wy * damp
        allp = allp + np.column_stack([wx, wy])
        k = 0
        for pts, z1, z2, q, rcell, i in segs:
            polys[i] = allp[k:k + len(pts)]
            k += len(pts)
        # waterfalls to keep where the coarse river drops steeply (knickpoints())
        ws_c = np.where(ctx.elev > 0, ctx.elev, 0.0)
        if len(ctx.clvl):
            ws_c = np.where(ctx.lake_c, ctx.clvl[np.maximum(ctx.clab, 0)], ws_c)
        cover_all = ctx.L.get("sediment_cover", np.zeros(ctx.g.n))
        srock = ctx.L.get("surface_rock", ctx.L["rock"])
        ctx.kps = RG.knickpoints(ws_c, ctx.down, riv, ctx.elev > 0, ctx.flow * ctx.cell_area * RG.KM2_M_PER_YR_TO_M3S,
                          {c: float(arc_km(ctx.g.centers[c] @ ctx.g.centers[ctx.down[c]]))
                           for c in polys}, polys,
                          {c: (int(srock[c]), int(ctx.rock[c]), float(cover_all[c]),
                               *((float(ctx.L["strata_top_km"][c]), int(ctx.L["strata_next"][c])) if "strata_next" in ctx.L else ()))
                           for c in polys})
        # Along a reach with falls the valley floor becomes a staircase: the
        # floor between the falls is graded at what's left of the reach's
        # slope, and drops by each fall's height at its lip.
        zseg = {i: (z1, z2) for _, z1, z2, _, _, i in segs}
        stair = {}

        def scarp_fall(kp, Tz, Ez, pix, inr):
            """A designed reach crossing a landform's scarp (an escarpment):
            the hard bed holds the river on the plateau down to the scarp, so
            the valley floor and the ground above the crossing stand at the
            scarp's level, and the main fall takes (up to) the scarp's
            height, its lip retreated from the crossing by its gorge."""
            ws_, lv_, hg_ = (np.where(inr, a[np.where(inr, pix, 0)], 0.0) for a in ctx.scarp)
            on = ws_ > RG.SCARP_MIN_W
            a_ = np.flatnonzero(on & (Ez >= lv_))
            if not len(a_):
                return
            b_ = np.flatnonzero(on & (Ez < lv_) & (np.arange(len(Ez)) > a_[0]))
            if not len(b_):
                return
            j = int(b_[0])
            sk = kp["s"]
            st0 = kp["steps"][0]
            # (the lip on a point of the reach's polyline, so the staircase's
            # floor at it is the gorge's, not half the plateau's)
            k = int(np.searchsorted(sk, max(sk[j] - st0["gorge_km"], 0.0)))
            s_lip = float(sk[min(k, j)])
            foot = float(Tz[min(k, j)])  # (the gorge's floor below the lip: the lowland's)
            up = sk < s_lip
            # above the lip the river runs on the plateau (its floor graded up
            # from the lip), and the ground stands at the scarp's level down to
            # the crossing (the gorge's walls)
            Tz[up] = np.maximum(Tz[up], np.minimum(float(lv_[j]), Ez[up]) + RG.KP_GRADED * (s_lip - sk[up]))
            Ez[sk <= sk[j]] = np.maximum(Ez[sk <= sk[j]], np.maximum(Tz[sk <= sk[j]], lv_[j]) + 1.0)
            st0["s"], st0["gorge_km"] = s_lip, float(sk[j] - s_lip)
            st0["h"] = max(st0["h"], float(ws_[j] * hg_[j]), float(lv_[j]) - foot)
            n = len(kp["steps"])  # (the cascades: spread down the reach below the scarp again)
            for c_, st in enumerate(kp["steps"][1:], 1):
                st["s"] = float(sk[j] + c_ / n * (sk[-1] - sk[j]))
            kp["scarp"] = True

        for kp in ctx.kps:
            cells, sk, m = kp["cells"], kp["s"], kp["m"]
            Tz = np.concatenate([np.linspace(*zseg[c], m)[(1 if j else 0):] for j, c in enumerate(cells)])
            Ez = np.concatenate([np.linspace(ws_c[c], ws_c[ctx.down[c]], m)[(1 if j else 0):] for j, c in enumerate(cells)])
            line = np.concatenate([polys[c] if j == 0 else polys[c][1:] for j, c in enumerate(cells)])
            # (the valley floor near the zoom's coast: see z_course)
            lc = np.floor(line[:, 0] / ctx.res + ctx.nx / 2).astype(int)
            lr = np.floor(ctx.ny / 2 - line[:, 1] / ctx.res).astype(int)
            inr = (lc >= 0) & (lc < ctx.nx) & (lr >= 0) & (lr < ctx.ny)
            Tz[inr] = np.minimum(Tz[inr], coast_cap[(lr * ctx.nx + lc)[inr]])
            # (a landform's plateau stands above the coarse ground: the falls may too)
            if ctx.ground_up is not None:
                wl, lv = (a[(lr * ctx.nx + lc)[inr]] for a in ctx.ground_up)
                Ez[inr] += wl * np.maximum(lv - Ez[inr], 0.0)
            if ctx.scarp is not None:
                scarp_fall(kp, Tz, Ez, (lr * ctx.nx + lc), inr)
            # the river keeps to the reach's course (receivers pinned along it, in the landscape pass)
            pp, pa = RG._raster_path(line, ctx.res, ctx.nx, ctx.ny)
            kp["course_px"], kp["course_s"] = pp[pp >= 0], pa[pp >= 0]
            # (and the main river above the reach, so its water arrives at the top of the course)
            ups_, u = [], up_main.get(cells[0])
            while u is not None and u in polys and len(ups_) < 8:
                ups_.append(polys[u])
                u = up_main.get(u)
            for q_ in [pp] + [RG._raster_path(pl, ctx.res, ctx.nx, ctx.ny)[0] for pl in ups_]:
                ctx.pin_pairs += [(a, b) for a, b in zip(q_[:-1], q_[1:])
                              if a >= 0 and b >= 0 and abs(a // ctx.nx - b // ctx.nx) <= 1 and abs(a % ctx.nx - b % ctx.nx) <= 1]
            drop = Tz[0] - Tz[-1]
            Hs = np.array([st["h"] for st in kp["steps"]])
            scale = min(1.0, 0.85 * max(drop, 0.0) / max(Hs.sum(), 1e-9))
            for st in kp["steps"]:
                st["h"] *= scale
            # the plateau above each fall must fit in the valley (staircase())
            kp["fit"] = RG.staircase(kp, Tz, Ez)
            Z = RG.stair_z(kp, sk)
            for j, c in enumerate(cells):
                stair[c] = (kp, j, Z[j * (m - 1):(j + 1) * (m - 1) + 1])
        # A tributary joining a reach with falls joins it at the staircase's
        # level (on the plateau above a fall), not at the valley floor below
        # it: else its valley is a trench below the main river, which spills
        # into it and leaves its course. Raised floors carry on upstream.
        zseg = {i: [z1, z2] for _, z1, z2, _, _, i in segs}
        ups = {}
        for i in zseg:
            ups.setdefault(ctx.down[i], []).append(i)
        todo = [(i, stair[ctx.down[i]][2][0]) for i in zseg if ctx.down[i] in stair and i not in stair]
        while todo:
            i, zj = todo.pop()
            if i in stair or zj <= zseg[i][1]:
                continue
            zseg[i][1] = zj
            zseg[i][0] = max(zseg[i][0], zj)
            todo += [(u, zseg[i][0]) for u in ups.get(i, [])]
        segs = [(pts, *zseg[i], q, rcell, i) for pts, _, _, q, rcell, i in segs]
        pin_px = np.array([a for a, b in ctx.pin_pairs if 3 <= a // ctx.nx < ctx.ny - 3 and 3 <= a % ctx.nx < ctx.nx - 3], dtype=np.int64)
        k = 0
        ax, ay, bx, by, za, zb, fw, wall, reach, sq, kseg, s0seg = ([] for _ in range(12))
        half = ctx.size_km / 2 - 4 * ctx.res
        for pts, z1, z2, q, rcell, i in segs:
            m = len(pts)
            pw = allp[k:k + m]
            k += m
            zz = stair[i][2] if i in stair else np.linspace(z1, z2, m)
            if i in stair:  # sub-segments of a reach with falls: which one, and arc length along it
                kp, j, _ = stair[i]
                kseg += [ctx.kps.index(kp)] * (m - 1)
                s0seg += list(kp["s"][j * (m - 1):(j + 1) * (m - 1)])
            else:
                kseg += [-1] * (m - 1)
                s0seg += [0.0] * (m - 1)
            qm3 = q * RG.KM2_M_PER_YR_TO_M3S
            w_floor = max(0.8 * ctx.res, 0.4 + 0.6 * np.log10(1 + qm3 / 50))
            s_wall = 30 + 170 * rcell
            ax += list(pw[:-1, 0]); ay += list(pw[:-1, 1]); bx += list(pw[1:, 0]); by += list(pw[1:, 1])
            za += list(zz[:-1]); zb += list(zz[1:])
            fw += [w_floor] * (m - 1); wall += [s_wall] * (m - 1)
            reach += [w_floor + min(2500 / s_wall, 40)] * (m - 1)
            sq += [q] * (m - 1)
            ctx.river_segs.append(pw)
            ctx.inside = (np.abs(pw[:, 0]) < half) & (np.abs(pw[:, 1]) < half)
            in_r = (np.abs(pw[:, 0]) < ctx.size_in / 2) & (np.abs(pw[:, 1]) < ctx.size_in / 2)
            ctx.n_rivers_in += bool(np.any(in_r[1:] & ~in_r[:-1]) and not in_r[0])
            # entering the built area from outside: bring the coarse discharge in
            j = np.flatnonzero(ctx.inside[1:] & ~ctx.inside[:-1])
            if len(j) and not ctx.inside[0]:
                p = pw[j[0] + 1]
                col = int(np.clip(np.floor(p[0] / ctx.res + ctx.nx / 2), 3, ctx.nx - 4))
                row = int(np.clip(np.floor(ctx.ny / 2 - p[1] / ctx.res), 3, ctx.ny - 4))
                if len(pin_px):  # onto a pinned course (of a reach with falls) if it runs here
                    pr, pc = np.divmod(pin_px, ctx.nx)
                    dk = np.maximum(np.abs(pr - row), np.abs(pc - col))
                    if dk.min() <= 4:
                        row, col = (int(v) for v in divmod(int(pin_px[np.argmin(dk)]), ctx.nx))
                ctx.inflow[row * ctx.nx + col] += q
                ctx.inflow_pts.append((row * ctx.nx + col, int(min(np.ceil((w_floor + min(2500 / s_wall, 40)) / ctx.res) + 2, 30))))
        arr = lambda v: np.ascontiguousarray(v, dtype=float)
        T, D, I = ZK.carve_segments(ctx.nx, ctx.ny, ctx.xs[0], ctx.ys[0], ctx.res, arr(ax), arr(ay), arr(bx), arr(by),
                                    arr(za), arr(zb), arr(fw), arr(wall), arr(reach))
        on = (I >= 0) & (D < np.maximum(arr(fw)[np.maximum(I, 0)], 0.75 * ctx.res))
        ctx.riv_q = np.where(on, arr(sq)[np.maximum(I, 0)], 0.0)
        ctx.cut = ctx.land & np.isfinite(T)
        h_uncut = ctx.h
        ctx.h = np.where(ctx.cut, RG.smin(ctx.h, np.where(np.isfinite(T), T, 1e9), 40.0), ctx.h)
        ctx.h = ctx.clamp(ctx.h)
        ctx.carved = np.minimum(ctx.h - h_uncut, 0.0)
        # the coarse river keeps at least its valley floor (the staircase, on
        # reaches with falls) in the landscape pass, wherever its water runs:
        # the floor of the nearest point of its polyline
        Ii = np.maximum(I, 0)
        sa, sb_ = arr(za)[Ii], arr(zb)[Ii]
        vx, vy = arr(bx)[Ii] - arr(ax)[Ii], arr(by)[Ii] - arr(ay)[Ii]
        tt = np.clip(((ctx.px - arr(ax)[Ii]) * vx + (ctx.py - arr(ay)[Ii]) * vy) / np.maximum(vx * vx + vy * vy, 1e-12), 0, 1)
        zc = sa + tt * (sb_ - sa)
        # on reaches with falls: the staircase, evaluated at the arc length of
        # the nearest polyline point, so each fall is a sharp step wherever
        # the fine river crosses it
        ctx.kpix = np.where(I >= 0, np.asarray(kseg, int)[Ii], -1)
        ctx.s_pix = arr(s0seg)[Ii] + tt * np.hypot(vx, vy)
        for k_, kp in enumerate(ctx.kps):
            on_k = ctx.kpix == k_
            if on_k.any():
                zc[on_k] = RG.stair_z(kp, ctx.s_pix[on_k])
        ctx.z_course = np.where(ctx.land & (I >= 0) & (D < arr(reach)[Ii]), zc, -np.inf)
        # ... but no higher than a gentle ramp up from the zoom's own coast,
        # which may lie inland of the coarse one: else the river is held at
        # the coarse valley floor right to the sea and drops into it off a cliff
        # (a reach with falls has it in its valley floor already: staircase())
        ctx.z_course = np.where(ctx.kpix < 0, np.minimum(ctx.z_course, coast_cap), ctx.z_course)
        ctx.bottom = D < np.maximum(arr(fw)[Ii], ctx.res) + 2 * ctx.res  # the valley bottom along the polyline
        ctx.q_course = np.where(I >= 0, arr(sq)[Ii], np.inf)
    # smaller coarse streams crossing into the region bring their water too
    half = ctx.size_km / 2 - 4 * ctx.res
    inner = in_sel & (ctx.elev > 0) & (ctx.down >= 0) & ~riv
    for i in np.flatnonzero(inner):
        d = ctx.down[i]
        if ctx.elev[d] <= 0 or ctx.flow[i] <= 0:
            continue
        a, b = ctx.fr.to_plane(ctx.g.centers[[i, d]])
        ins = (np.abs(a) < half) & (np.abs(b) < half)
        if ins[0] or not ins[1]:
            continue
        t = np.linspace(0, 1, 64)
        xx, yy = a[0] + t * (a[1] - a[0]), b[0] + t * (b[1] - b[0])
        k = int(np.argmax((np.abs(xx) < half) & (np.abs(yy) < half)))
        col = int(np.clip(np.floor(xx[k] / ctx.res + ctx.nx / 2), 3, ctx.nx - 4))
        row = int(np.clip(np.floor(ctx.ny / 2 - yy[k] / ctx.res), 3, ctx.ny - 4))
        ctx.inflow[row * ctx.nx + col] += ctx.flow[i] * ctx.cell_area
        ctx.inflow_pts.append((row * ctx.nx + col, 3))
    ctx.log(f"  {len(ctx.riv_ids)} coarse river cells carved, {ctx.n_rivers_in} entering from outside "
        f"[{time.time() - ctx.t0:.1f}s]")


def categorical_layers(ctx):
    """Rock, climate and landform per pixel from the nearest coarse cell after a noisy warp.
    Reads: L, Pk, S, elev, fr, g, land, land_all, own, px, py, res, rock_f, sp, surf_f, vf.
    Writes: clim_f, form_f, land_all, rock_f, surf_f."""
    # --- categorical layers (nearest cell after a noisy warp) ------------
    lw = 0.5 * ctx.sp
    camp = 0.16 * ctx.sp / 0.17
    wxp = ZK.fbm(ctx.Pk, lw, RG._octaves(lw, 2 * ctx.res), 0.55, ctx.S + 21) * camp
    wyp = ZK.fbm(ctx.Pk, lw, RG._octaves(lw, 2 * ctx.res), 0.55, ctx.S + 22) * camp
    cell_w = ctx.g.locate(ctx.fr.to_sphere(ctx.px + wxp, ctx.py + wyp), ctx.own.astype(np.int64))
    # land pixels shouldn't pick up an ocean cell's attributes (and vice versa)
    ctx.land_all = ctx.elev > 0
    alt = np.arange(ctx.g.n)
    for i in np.unique(cell_w):
        nb = ctx.g.nbr_idx[ctx.g.nbr_off[i]:ctx.g.nbr_off[i + 1]]
        same = nb[ctx.land_all[nb] != ctx.land_all[i]]
        if len(same):
            alt[i] = same[np.argmax(np.abs(ctx.elev[same]))] if ctx.land_all[i] else same[np.argmax(ctx.elev[same])]
    mismatch = ctx.land != ctx.land_all[cell_w]
    cell_l = np.where(mismatch, alt[cell_w], cell_w)
    ctx.rock_f = ctx.L["rock"][cell_l].astype(np.uint8)
    ctx.surf_f = ctx.L.get("surface_rock", ctx.L["rock"])[cell_l].astype(np.uint8)
    ctx.clim_f = ctx.L.get("climate", np.full(ctx.g.n, RG.SEA_CLIMATE))[cell_l].astype(np.uint8)
    ctx.form_f = np.asarray(ctx.L["landform"])[cell_l].astype(np.uint8) if "landform" in ctx.L else None
    if ctx.vf is not None:  # the volcanoes' own rock, and their reefs' limestone
        ctx.rock_f = np.where(ctx.vf["rock"] > 0, ctx.vf["rock"], ctx.rock_f).astype(np.uint8)
        ctx.surf_f = np.where(ctx.vf["reef"], RG.LIMESTONE, np.where(ctx.vf["rock"] > 0, ctx.vf["rock"], ctx.surf_f)).astype(np.uint8)
