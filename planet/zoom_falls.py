"""Carved waterfalls (PW-517): a tall drop in the zoom's ground becomes a fall
with a form, not a sheer wall one pixel wide.

The landscape pass can leave a river dropping a kilometre in a pixel or two
(a basin on high ground spilling over its rim into a valley graded from the
sea). Real falls this tall are tiered and sit at the head of a gorge: the
lip has retreated upstream into the plateau, leaving ledges where the harder
beds were, a plunge basin at the foot, and walls that open out round it.
carve() finds each steep run of a river (>= FALL_SLOPE over consecutive links,
>= FALL_MIN_M in all, carrying >= FALL_MIN_Q m^3/s) and, keeping its total
drop, redraws it:

- the knickpoint's retreat: the bed is lowered over a gorge upstream of the
  old lip, the length growing with the drop and the discharge (a bigger drop
  and more water cut back further), until it meets the plateau;
- tiers: the drop is split into n steps (each at most TIER_M m, scaled to the
  planet's relief), the highest at the lip and the rest falling off by
  TIER_SHARE, with ledges (rapids) between them taking the rest of the drop;
- walls: the ground is cut to a cone of WALL_SLOPE m/km rising from every
  bed pixel, so the ground beside the lip is no higher than the walls of the
  gorge it feeds (no flat platform jutting up round the lip), and round the
  foot the same cones make a funnel, an amphitheatre, the plunge basin's rim;
  the horseshoe comes from the walls closing in on the lip's pixels;
- ledges are not level: the walls' slope varies with the bed's tier (a
  hard tier stands steeper) so the face is irregular, not planar.

Everything only lowers the ground, except where a bed pixel below a tier is
brought up to the new profile (at most the profile's own small rise).
"""
from __future__ import annotations

import numpy as np

FALL_SLOPE = 0.12      # m/m: a link this steep (7 deg) is part of a fall
FALL_MIN_M = 100.0     # m: ... at least this much drop in all, at Earth's relief
FALL_MIN_Q = 20.0      # m^3/s
EARTH_RELIEF_M = 6000.0  # land p99 the thresholds below scale with
TIER_M = 300.0         # m: a single step is at most this high (at Earth's relief)
TIER_SHARE = 0.6       # each tier below the lip's is this much of the one above
TIER_FRAC = 0.65       # the share of the drop taken in steps (the rest: rapids between them)
GORGE_KM_PER_KM = 12.0  # km of gorge upstream per km of drop (at 50 m^3/s), x (Q/50)^0.25
GORGE_MAX_KM = 30.0
WALL_SLOPE = (0.55, 1.1)  # m/m of the walls' cones: soft .. hard tier (29 .. 48 deg)
MAX_FALLS = 12


def tier_plan(D, sc, given=None):
    """The steps (m, the lip's first) a drop of D m is split into: each at most TIER_M x sc, the next
    TIER_SHARE x the one above, together TIER_FRAC of the drop (the rest is rapids between them).
    given: the steps the coarser zoom already placed; kept in proportion, rescaled to this drop."""
    if given is not None and len(given):
        g = np.asarray(given, float)
        return TIER_FRAC * D * g / g.sum()
    n_t = int(np.clip(np.ceil(TIER_FRAC * D / (TIER_M * sc)), 1, 6))
    w = TIER_SHARE ** np.arange(n_t)
    return TIER_FRAC * D * w / w.sum()


FACE_DEG = (74.0, 86.0)  # a tier's face: near vertical rock, in sub-steps with ledges between
RAPID_GRAD = 0.3         # m/m of the rapids between tiers
LEDGE_FRAC = 0.2         # a ledge between a face's sub-steps: this much of the sub-step's height long
RECESS_FRAC = 0.9        # a horseshoe lip's centre is cut back this much of the first tier's height (m per m), 15 .. 500 m
POOL_RADIUS_FRAC = 0.12  # a tier's plunge pool: radius as a share of the tier's height (at least the river's)


def fine_profile(top, bottom, tiers, s0, rng, room_km):
    """The floor of a fall at a fine zoom's scale, along the river from the lip (s = 0, km): the
    knots (s, z) of tiers split into 1-3 sub-steps (a face of near-vertical rock with ledges
    between, irregular), each followed by rapids, ending at `bottom` exactly (the parent's drop is
    kept) at room_km: the parent's fall spans its whole gorge, so the rapids take the length the
    faces leave. Returns (s, z, foots) with foots = [(s, z, tier m)] (the foot of each tier)."""
    H = top - bottom
    tiers = np.asarray(tiers, float)
    n = len(tiers)
    rap = max(H - tiers.sum(), 0.0)
    pieces = []  # per tier: (ds km, dz m) of its sub-steps and ledges
    for t in tiers:
        k = int(np.clip(np.ceil(t / 120.0), 1, 3))
        fr = rng.dirichlet(np.full(k, 3.0)) * t
        pc = []
        for q, f_ in enumerate(fr):
            pc.append((f_ / np.tan(np.radians(rng.uniform(*FACE_DEG))) / 1000.0, f_))
            if q < k - 1:  # a ledge: nearly level, a little back-tilted
                led = LEDGE_FRAC * f_ / 1000.0 * rng.uniform(0.5, 1.5)
                pc.append((led, 0.04 * led * 1000.0))
        pieces.append(pc)
    fixed = s0 + sum(ds for pc in pieces for ds, _ in pc)
    avail = max(room_km - fixed, 0.25 * room_km)
    gaps = max(n - 1, 1)  # (rapids lie between the tiers; the last tier's foot is the parent's pool, at `bottom`)
    wts = tiers[:gaps] ** 0.5
    ln = avail * wts / wts.sum() if rap > 0 else np.zeros(gaps)
    ks, kz, foots = [0.0, s0], [top, top], []
    s, z = s0, top
    if n == 1 and rap > 0:  # (a lone tier: a rapids reach above its face)
        s += ln[0]
        z -= rap
        ks.append(s), kz.append(z)
    for j, pc in enumerate(pieces):
        for ds, dz in pc:
            s += ds
            z -= dz
            ks.append(s), kz.append(z)
        foots.append([s, z, float(tiers[j])])
        if j < n - 1:
            s += ln[j]
            z -= rap / (n - 1)
            ks.append(s), kz.append(z)
    ks, kz = np.array(ks), np.array(kz)
    if ks[-1] > room_km:  # a short gorge: the whole stepped reach squeezed into it
        f = room_km / ks[-1]
        ks = ks * f
        for ft in foots:
            ft[0] *= f
    g = H / max(top - kz[-1], 1e-9)  # (the ledges' tilt took a little: the drop is the parent's exactly)
    kz = top - (top - kz) * g
    return ks, kz, [(a, top - (top - b) * g, c) for a, b, c in foots]


def horseshoe(d_km, t1_m, half_km):
    """How far downstream (km) a lip's crest is held at lateral distance d from the river: none at the
    river (the lip itself), RECESS x the first tier's height at the flanks, from half_km (the gorge's
    half width at the lip) x 1.3 out: the crest curves round the head of the gorge, centre upstream,
    flanks downstream (Niagara's horseshoe, Kaieteur's bowl). Returns (lag(d), R0, T)."""
    R0 = float(np.clip(RECESS_FRAC * t1_m, 15.0, 500.0)) / 1000.0
    T = 1.3 * half_km
    return R0 * np.clip((d_km / T) ** 2, 0.0, 1.0), R0, T


def _accumulate(rec, order, src):
    acc = src.copy()
    for i in order[::-1]:
        r = rec[i]
        if r >= 0:
            acc[r] += acc[i]
    return acc


def carve(h, hfill, rec, order, active, q_src, nx, ny, res, seed=0):
    """(new ground, list of dicts for the carved falls, [(pixel, depth m)] of the plunge basins below the tiers). h: ground, hfill: its
    depression-filled surface (what the rivers will run over), rec/order: D8
    receivers and order outlet -> headwater on it, q_src: discharge each pixel
    adds (m^3/s), active: land the pass shapes. Pixel scale: res km."""
    n = nx * ny
    top_ref = float(np.percentile(h[active], 99)) if active.any() else EARTH_RELIEF_M
    sc = float(np.clip(top_ref, 1500.0, 12000.0) / EARTH_RELIEF_M)
    z = np.maximum(h, hfill)  # (the surface the rivers run over: pits are filled)
    Q = _accumulate(rec, order, q_src)
    idx = np.arange(n)
    has = rec >= 0
    rr = np.where(has, rec, 0)
    diag = (rr % nx != idx % nx) & (rr // nx != idx // nx)
    dist = res * np.where(diag, 1.4142, 1.0)
    dh = np.where(has, z - z[rr], 0.0)
    steep = has & (dh >= FALL_SLOPE * dist * 1000.0) & (Q >= FALL_MIN_Q) & active
    e = 8
    row, col = idx // nx, idx % nx
    inner = (row >= e) & (row < ny - e) & (col >= e) & (col < nx - e)
    # main donor per pixel (the biggest)
    main_up = np.full(n, -1)
    o = np.argsort(Q, kind="stable")
    o = o[has[o]]
    main_up[rec[o]] = o
    runs = []
    for i in np.flatnonzero(steep & inner):
        u = main_up[i]
        if u >= 0 and steep[u]:
            continue  # not the top of its run
        chain, p = [int(i)], int(i)
        while steep[p] and len(chain) < 40:
            p = int(rec[p])
            if p < 0 or not steep[p]:
                break
            chain.append(p)
        foot = int(rec[chain[-1]])
        if foot < 0:
            continue
        H = float(z[chain[0]] - z[foot])
        if H >= FALL_MIN_M * sc:
            runs.append((H * Q[chain[0]] ** 0.5, chain, foot, H))
    runs.sort(key=lambda t: -t[0])
    out = h.copy()
    info = []
    rng = np.random.default_rng(seed)
    wall_best = np.full(n, np.inf)
    # (an irregular face: the walls' slope varies from place to place, ledges and buttresses, not one plane)
    nz = rng.standard_normal((ny, nx))
    for _ in range(2):
        nz = (nz + np.roll(nz, 1, 0) + np.roll(nz, -1, 0)) / 3.0
        nz = (nz + np.roll(nz, 1, 1) + np.roll(nz, -1, 1)) / 3.0
    nz = (nz / max(float(nz.std()), 1e-9)).ravel()
    pools = []
    for _, chain, foot, H in runs[:MAX_FALLS]:
        Qf = float(Q[chain[0]])
        top = chain[0]
        # --- the chain: gorge upstream of the old lip, the old run, the foot
        L = float(np.clip(GORGE_KM_PER_KM * H / 1000.0 * (Qf / 50.0) ** 0.25 * np.sqrt(sc), 2.0, GORGE_MAX_KM))
        n_up = int(round(L / res))
        up = []
        p = top
        for _ in range(n_up):
            u = int(main_up[p])
            if u < 0 or not inner[u]:
                break
            up.append(u)
            p = u
        pix = np.array(up[::-1] + chain + [foot], dtype=np.int64)  # headwater -> foot
        M = len(pix)
        if M < 3:
            continue
        zt, zf = float(z[pix[0]]), float(z[foot])
        D = zt - zf
        if D <= 0:
            continue
        # profile from the foot (k = 0) up to the head (k = M - 1): rapids rising evenly...
        k = np.arange(M)[::-1].astype(float)  # (pix order is head -> foot: index 0 is the head)
        # tiers
        steps = tier_plan(D, sc)
        n_t = len(steps)
        # tier positions along the chain (index from the head): the lip's tier at the old lip
        # (len(up) in head -> foot order), the others spread below it over the old run and
        # the foot's reach
        lip_i = max(len(up) // 3, 0)  # (the new lip is the head of the gorge, tiers spread down it)
        pos = [1 + int(round(j * (M - 3) / n_t)) for j in range(n_t)]
        pos = sorted(set(min(max(p_, 1), M - 2) for p_ in pos))
        steps = steps[:len(pos)]
        prof = np.empty(M)
        rap = (D - steps.sum()) / max(M - 1, 1)  # the rapids' share, spread evenly per link
        zc = zt  # walk head -> foot
        prof[0] = zt
        stepmap = {p_: s for p_, s in zip(pos, steps)}
        for m in range(1, M):
            zc -= rap
            if m in stepmap:
                zc -= stepmap[m]
            prof[m] = zc
        prof[-1] = zf
        prof = np.minimum(prof, zt)
        tier = np.zeros(M, int)
        for j, p_ in enumerate(pos):
            tier[p_:] = j + 1
        # --- walls: cones of the bed pixels (hard tiers steeper), only lowering
        r_win = int(np.ceil(D / 1000.0 / WALL_SLOPE[0] / res)) + 3
        r_win = min(r_win, 14)
        for m in range(M):
            pm = int(pix[m])
            r0, c0 = divmod(pm, nx)
            a, b = max(r0 - r_win, 0), min(r0 + r_win + 1, ny)
            c, d = max(c0 - r_win, 0), min(c0 + r_win + 1, nx)
            rr_, cc_ = np.mgrid[a:b, c:d]
            dd = res * np.hypot(rr_ - r0, cc_ - c0)
            s_m = WALL_SLOPE[0] + (WALL_SLOPE[1] - WALL_SLOPE[0]) * ((tier[m] % 2) * 0.6 + rng.random() * 0.4)
            irr = 1.0 + 0.3 * np.clip(nz.reshape(ny, nx)[a:b, c:d], -2.0, 2.0)
            env = prof[m] + s_m * 1000.0 * irr * np.maximum(dd - 0.5 * res, 0.0)
            sl = (slice(a, b), slice(c, d))
            wb = wall_best.reshape(ny, nx)
            wb[sl] = np.minimum(wb[sl], env)
        out_ = out
        out_[pix] = np.minimum(out_[pix], prof)
        # the bed itself: at the profile (the filled surface under a pit was higher)
        out_[pix] = np.where(z[pix] > prof, prof, out_[pix])
        for j, p_ in enumerate(pos):  # a plunge basin below each tier of any size
            if steps[j] >= 40.0 * sc:
                pools.append((int(pix[min(p_ + 1, M - 1)]), float(np.clip(0.3 * steps[j], 5.0, 60.0))))
        info.append({"px": [int(pix[pos[0]] // nx), int(pix[pos[0]] % nx)], "drop_m": round(D, 1), "tiers": len(pos),
                     "gorge_km": round(len(up) * res, 1), "tier_m": [round(float(s), 1) for s in steps]})
    new = np.where(active & np.isfinite(wall_best), np.minimum(out, np.maximum(wall_best, 0.5)), out)
    # (the bed pixels are on their profile: the cones are at most the profile there)
    new = np.where(active, np.maximum(new, np.where(np.isfinite(wall_best), 0.5, -np.inf)), new)
    return new, info, pools
