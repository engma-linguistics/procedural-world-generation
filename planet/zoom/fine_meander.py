"""Meander trains of a fine zoom's alluvial rivers (PW-425).

zoom.fine._courses draws a single-thread alluvial reach as its valley axis
plus a meander train. PW-405 drew it as a sine-generated curve (Langbein &
Leopold 1966) of one wavelength and one swing: the same bend over and over,
a drawn wave. Here each bend is its own:

- its shape is Kinoshita's curve (direction theta = w sin phi + w^3 (Js cos
  3 phi - Jf sin 3 phi) along the channel, phi its phase: Kinoshita 1961,
  Parker et al. 1983): w the swing, Js the skew (bends leaning down- or
  up-valley), Jf the flatness (fattened apexes; past Jf ~ 1/(3 w^2) the apex
  turns back on itself: a compound, double-headed loop);
- w, Js, Jf and the bend's arc length vary from bend to bend: planet-fixed
  noise in the channel phase phi (phi itself is the parent network's
  planet-fixed valley phase psi, warped), so sibling and nested zooms draw
  the same bends;
- a bend's valley length follows its swing (a tight loop takes little
  valley for its arc: lambda_valley ~ (its curve's valley length per arc)
  ^ARC_P), plus ARC_VAR scatter: wavelengths scatter by ~+-30% about the
  reach's (MEANDER_WL widths), a big loop's neighbours stretch. The warp
  phi(psi) keeps the mean wavelength over every BLOCK wavelengths, which
  keeps it local (a point's phi depends only on psi near it);
- the swing is capped where the valley floor leaves no room (its amplitude),
  where a loop's neck would close (NECK) and, in zoom.fine._courses, where
  the centreline would bend tighter than R_MIN (a loop meeting a valley
  bend: PW-424).

A centreline is the valley axis B(s) plus, at each axis sample, the offset
X_loc (xi t + y n) of the curve's table point at phi (xi along the axis, y
across it). Its state per sample: (psi, phi, w, Js, Jf, X_loc): what a time
pass (PW-416) can evolve (bends growing: w up; migrating down-valley: phi
shifted; cutting off where the neck closes).
"""

from __future__ import annotations

import numpy as np

OMEGA_MAX = 1.95  # rad: a bend's largest swing (a sine-generated loop closes at ~2.2)
SWING = (1.0, 0.3, 0.75)  # a bend's swing / MEANDER_OMEGA: base + var x N + big x max(N, 0)^3 (N noise -1..1)
SKEW = 1.0 / 12.0  # Js at most (either way)
FLAT = (-0.015, 0.135)  # Jf: base + big x max(N, 0)^2
ARC_VAR = 0.3  # a bend's arc length scatter
ARC_P = 0.6  # a bend's valley length ~ (its curve's valley length per arc / the typical one's)^ARC_P
BLOCK = 3  # wavelengths: the warp keeps the mean wavelength over each block of this many
NECK = (1.2, 3.0)  # a loop's neck: its centrelines at least this many widths + px apart
R_MIN = (1.5, 2.5)  # the centreline's tightest bend radius: widths, px (real bends: ~2-3 widths, rarely under 1.5)
CUT_OM = 1.6  # rad: a loop swinging this far (its own swing, room allowing) may have cut off before (an oxbow) ...
CUT_P = 0.5  # ... with this chance; its new bend has CUT_W of its swing
CUT_W = 0.3
OXBOW_ARC = 0.4  # x pi: the old loop's arc either side of its apex kept as an oxbow

OM_G = np.linspace(0.0, 2.0, 41)
JS_G = np.array([-1.0, 0.0, 1.0]) * SKEW
JF_G = np.linspace(FLAT[0], FLAT[0] + FLAT[1], 4)
NPH = 256
_TAB = None


def _curve(w, js, jf, n=1024):
    phi = np.linspace(0.0, 2 * np.pi, n + 1)
    th = w * np.sin(phi) + w ** 3 * (js * np.cos(3 * phi) - jf * np.sin(3 * phi))
    dx, dy = np.cos(th), np.sin(th)
    ds = 2 * np.pi / n
    x = np.r_[0.0, np.cumsum(0.5 * (dx[1:] + dx[:-1]))] * ds
    y = np.r_[0.0, np.cumsum(0.5 * (dy[1:] + dy[:-1]))] * ds
    X = x[-1]
    y = y - np.trapezoid(y, x) / X  # (about its mean line)
    xi = x / X - phi / (2 * np.pi)
    xi -= xi[:-1].mean()
    rmin = 1.0 / max(np.abs(np.gradient(th, phi)).max(), 1e-9) / X
    m = 64
    k = np.arange(3 * m)
    p3 = (k % m) / m * 2 * np.pi
    xs = np.interp(p3, phi, x) + X * (k // m)
    ys = np.interp(p3, phi, y)
    D = np.hypot(xs[:, None] - xs[None], ys[:, None] - ys[None])
    neck = D[np.abs(k[:, None] - k[None]) >= 0.45 * m].min() / X
    pg = np.arange(NPH) / NPH * 2 * np.pi
    return np.interp(pg, phi, xi), np.interp(pg, phi, y / X), X, np.abs(y).max() / X, neck, rmin


def table():
    """Kinoshita curves over (w, Js, Jf): {xi, y: (.., NPH) along / across
    the axis per valley wavelength at channel phase phi; X: valley length
    per unit arc x 2 pi; amp: largest |y|; neck: closest approach of its
    limbs; rmin: tightest bend radius (all / its valley wavelength)}."""
    global _TAB
    if _TAB is None:
        sh = (len(OM_G), len(JS_G), len(JF_G))
        T = {k: np.zeros(sh + (NPH,)) for k in ("xi", "y")}
        T.update({k: np.zeros(sh) for k in ("X", "amp", "neck", "rmin")})
        for a, w in enumerate(OM_G):
            for b, js in enumerate(JS_G):
                for c, jf in enumerate(JF_G):
                    T["xi"][a, b, c], T["y"][a, b, c], T["X"][a, b, c], T["amp"][a, b, c], \
                        T["neck"][a, b, c], T["rmin"][a, b, c] = _curve(w, js, jf)
        _TAB = T
    return _TAB


def _corners(om, js, jf):
    out = []
    for v, g in ((om, OM_G), (js, JS_G), (jf, JF_G)):
        f = np.clip((np.asarray(v, float) - g[0]) / (g[1] - g[0]), 0.0, len(g) - 1.000001)
        i = np.floor(f).astype(int)
        out.append((i, f - i))
    return out


def prop(name, om, js, jf):
    """A table property (X, amp, neck, rmin) at (w, Js, Jf), multilinear."""
    T = table()[name]
    (a, ta), (b, tb), (c, tc) = _corners(om, js, jf)
    v = 0.0
    for da, wa in ((0, 1 - ta), (1, ta)):
        for db, wb in ((0, 1 - tb), (1, tb)):
            for dc, wc in ((0, 1 - tc), (1, tc)):
                v = v + wa * wb * wc * T[a + da, b + db, c + dc]
    return v


def shape(phi, om, js, jf):
    """(xi, y): the curve's offset along and across the axis / its valley
    wavelength at channel phase phi."""
    T = table()
    f = np.mod(phi, 2 * np.pi) / (2 * np.pi) * NPH
    i0 = np.floor(f).astype(int) % NPH
    i1, tf = (i0 + 1) % NPH, f - np.floor(f)
    (a, ta), (b, tb), (c, tc) = _corners(om, js, jf)
    out = []
    for k in ("xi", "y"):
        v = 0.0
        for da, wa in ((0, 1 - ta), (1, ta)):
            for db, wb in ((0, 1 - tb), (1, tb)):
                for dc, wc in ((0, 1 - tc), (1, tc)):
                    t_ = T[k][a + da, b + db, c + dc]
                    v = v + wa * wb * wc * ((1 - tf) * t_[np.arange(len(f)), i0] + tf * t_[np.arange(len(f)), i1])
        out.append(v)
    return out[0], out[1]


def _hash(k, seed):
    x = np.asarray(k, np.int64).astype(np.uint64) + np.full(np.shape(k), seed % (1 << 31), np.uint64) * np.uint64(0x9E3779B97F4A7C15)
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
    return (x >> np.uint64(11)).astype(float) / float(1 << 53) * 2.0 - 1.0


def noise(t, seed):
    """Smooth 1D value noise (Catmull-Rom through hashed knots at the
    integers), about -1..1."""
    t = np.asarray(t, float)
    i = np.floor(t).astype(np.int64)
    f = t - i
    p0, p1, p2, p3 = (_hash(i + d, seed) for d in (-1, 0, 1, 2))
    v = 0.5 * (2 * p1 + (p2 - p0) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (3 * p1 - p0 - 3 * p2 + p3) * f ** 3)
    return np.clip(v, -1.0, 1.0)


def params(phi, omega, seed):
    """A bend's own (w, Js, Jf) and arc length factor at channel phase phi
    (planet-fixed: noise in the bend count phi / 2 pi)."""
    b = np.asarray(phi, float) / (2 * np.pi)
    om = omega * (SWING[0] + SWING[1] * noise(b / 1.5, seed + 1) + SWING[2] * np.maximum(noise(b / 1.3, seed + 2), 0) ** 3)
    om = np.minimum(om, OMEGA_MAX)
    js = SKEW * noise(b / 2.2, seed + 3) * np.minimum(1.0, (1.3 / np.maximum(om, 1e-3)) ** 3)  # (Js w^3: at most
    # its value at w 1.3, or the skewed loops' limbs pinch)
    jf = FLAT[0] + FLAT[1] * np.maximum(noise(b / 1.7, seed + 4), 0) ** 2
    arc = 1.0 + ARC_VAR * noise(b / 1.2, seed + 5)
    return om, js, jf, arc


def _rate(phi, omega, seed, x_ref):
    om, js, jf, arc = params(phi, omega, seed)
    return (prop("X", om, js, jf) / x_ref) ** ARC_P * arc


def phase(psi, omega, seed):
    """The channel phase phi at valley phase psi (both rad), its bend's
    (w, Js, Jf), and the local valley wavelength / the reach's (h)."""
    psi = np.asarray(psi, float)
    x_ref = float(prop("X", omega, 0.0, 0.0))
    K2 = 2 * np.pi * BLOCK
    jb = np.floor(psi / K2).astype(np.int64)
    j0, j1 = int(jb.min()) - 1, int(jb.max()) + 1
    G = BLOCK * 48
    js_ = np.arange(j0, j1 + 1)
    ph_g = K2 * js_[:, None] + np.linspace(0.0, K2, G + 1)[None, :]
    r_g = _rate(ph_g.ravel(), omega, seed, x_ref).reshape(ph_g.shape)
    F = np.concatenate([np.zeros((len(js_), 1)), np.cumsum(0.5 * (r_g[:, 1:] + r_g[:, :-1]), 1)], 1)
    H = F[:, -1] / G  # (each block's mean rate)
    phi = np.empty_like(psi)
    for j in np.unique(jb):
        r = int(j - j0)
        sel = jb == j
        phi[sel] = np.interp(psi[sel], K2 * j + K2 * F[r] / F[r, -1], ph_g[r])
    om, js, jf, arc = params(phi, omega, seed)
    Hs = np.interp(psi, K2 * (js_ + 0.5), H)  # (the blocks' means, evened: no step in the swing between blocks)
    h = (prop("X", om, js, jf) / x_ref) ** ARC_P * arc / Hs
    return phi, om, js, jf, h


def train(psi, om_fac, lam, w, room, res, omega, seed):
    """A meander train's offsets at axis samples: (along, across) km, and its
    state (phi, w, Js, Jf, X_loc). psi: valley phase; om_fac: the share of
    its full swing the reach allows (0..1: alluvial, single-thread, drawn at
    this resolution, tapering out at the course's ends); lam: the reach's
    wavelength km; w: channel width km; room: the floor's room for its
    amplitude km (or None); res: km/px; omega: the typical swing."""
    phi, om_i, js_i, jf_i, h = phase(psi, omega, seed)
    Xl = lam * h
    om0 = om_i * om_fac
    om, js, jf = om0.copy(), js_i.copy(), jf_i.copy()
    if room is not None:
        # (a reach with little room: all its bends smaller, the big ones still the biggest; then none past it)
        sc = np.ones_like(om)
        for _ in range(4):
            big = belt_amp(om_fac * omega * sc, omega) / (1 + ARC_VAR) * lam
            sc = sc * np.clip(room / np.maximum(big, 1e-12), 0.3, 1.0) ** 0.7
        om = om * sc
        for _ in range(4):
            a = prop("amp", om, js, jf) * Xl
            om = np.where(a > room, om * np.clip(room / np.maximum(a, 1e-12), 0.5, 1.0), om)
    # no bend tighter than R_MIN: its skew and flatness let down first (they pinch a bend's apex or limbs),
    # then its swing
    r_lo = 1.3 * np.maximum(R_MIN[0] * w, R_MIN[1] * res)  # (x 1.3: the bends' own changes tighten them)
    for _ in range(8):
        bad = prop("rmin", om, js, jf) * Xl < r_lo
        if not bad.any():
            break
        flat = bad & (np.abs(js) < 0.1 * SKEW) & (jf < 0.1 * FLAT[1])
        js = np.where(bad, 0.6 * js, js)
        jf = np.where(bad, np.minimum(jf, 0.6 * jf), jf)
        om = np.where(flat, np.maximum(om - 0.05, 0.0), om)
    need = NECK[0] * w + NECK[1] * res
    for _ in range(12):
        bad = prop("neck", om, js, jf) * Xl < need
        if not bad.any():
            break
        om = np.where(bad, np.maximum(om - 0.05, 0.0), om)
    # (the caps as shares, evened over a quarter wavelength: a step in a bend's swing would be a step in
    # its offset)
    dps = np.abs(np.diff(psi))
    half = max(1, int(0.25 * 2 * np.pi / max(float(np.median(dps)) if len(dps) else 1.0, 1e-9)))
    om = om0 * _ease(np.where(om0 > 1e-6, om / np.maximum(om0, 1e-6), 1.0), half)
    js = js_i * _ease(np.where(np.abs(js_i) > 1e-9, js / np.where(np.abs(js_i) > 1e-9, js_i, 1.0), 1.0), half)
    jf = np.minimum(jf_i, FLAT[0] + (jf_i - FLAT[0]) * _ease(np.where(jf_i - FLAT[0] > 1e-9, (jf - FLAT[0]) / np.maximum(jf_i - FLAT[0], 1e-9), 1.0), half))
    # cutoffs: a half-bend (its apex at phi = k pi) swinging past CUT_OM (its neck closing) cut through it
    # once (planet-fixed chance CUT_P): the river runs a smaller bend there (its swing let down to CUT_W over
    # the bend and its neighbours' halves), its old loop an oxbow
    k = np.round(phi / np.pi).astype(np.int64)
    d = phi - np.pi * k
    tight = (om_i * om_fac > CUT_OM) & (om > 1.2) & (np.abs(d) < 0.25 * np.pi)
    ku, inv = np.unique(k, return_inverse=True)
    cut_k = np.zeros(len(ku), bool)
    np.logical_or.at(cut_k, inv, tight)
    cut_k &= _hash(ku, seed + 6) < 2 * CUT_P - 1
    old = None
    if cut_k.any():
        xo, yo = shape(phi, om, js, jf)
        old = (Xl * xo, Xl * yo, cut_k[inv] & (np.abs(d) < OXBOW_ARC * np.pi))
        cut_set = set(ku[cut_k].tolist())
        r = np.ones_like(om)
        for dk in (-1, 0, 1):
            on = np.array([int(v) in cut_set for v in (k + dk)])
            dd = phi - np.pi * (k + dk)
            r = np.where(on & (np.abs(dd) < np.pi), r * (1.0 - (1.0 - CUT_W) * np.cos(0.5 * dd) ** 2), r)
        om = om * r
    xi, y = shape(phi, om, js, jf)
    return Xl * xi, Xl * y, {"phi": phi, "omega": om, "js": js, "jf": jf, "X": Xl, "oxbow": old}


def _ease(r, half):
    """A share (0..1) per sample, eased: its running minimum over +-half
    samples, smoothed over half of that (never above the minimum's)."""
    r = np.clip(np.asarray(r, float), 0.0, 1.0)
    if len(r) < 3:
        return r
    p = np.pad(r, half, mode="edge")
    m = np.lib.stride_tricks.sliding_window_view(p, 2 * half + 1).min(1)
    sg = max(0.5 * half, 0.5)
    k = np.arange(-int(np.ceil(3 * sg)), int(np.ceil(3 * sg)) + 1)
    g = np.exp(-0.5 * (k / sg) ** 2)
    g /= g.sum()
    return np.convolve(np.pad(m, len(k) // 2, mode="edge"), g, "valid")


def belt_amp(om_b, omega):
    """The largest amplitude / wavelength a reach allowing swing om_b
    (0..omega) can draw (its biggest bends): for the meander belt."""
    om = np.minimum(np.asarray(om_b, float) * (SWING[0] + SWING[1] + SWING[2]), OMEGA_MAX)
    x_ref = float(prop("X", omega, 0.0, 0.0))
    return prop("amp", om, 0.0, 0.0) * (prop("X", om, 0.0, 0.0) / x_ref) ** ARC_P * (1 + ARC_VAR)
