"""PW-950: the sea floor's sediment cover creeps down its slope (surface._creep, clinoform diffusion)."""
import numpy as np

from planet import surface
from planet.grid import build_grid
from planet.tectonics.params import Params


def _sea_edges(g, sea):
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    m = sea[ea] & sea[eb]
    return ea[m], eb[m]


def _step(g):
    """A shelf at -100 m with 3 km of cover on one hemisphere, bare abyssal floor at -4000 m on the other."""
    shelf = g.centers[:, 0] > 0
    h = np.where(shelf, -100.0, -4000.0)
    cover = np.where(shelf, 3.0, 0.0)
    return shelf, h, cover


def test_creep_conserves_sediment_and_never_overdraws():
    g = build_grid(4)
    rng = np.random.default_rng(1)
    h = rng.uniform(-5000, -50, g.n)
    avail = rng.uniform(0, 0.05, g.n) * (rng.random(g.n) < 0.7)
    iso = rng.uniform(150, 260, g.n)
    ea, eb = _sea_edges(g, np.ones(g.n, bool))
    net = surface._creep(h, iso, avail, ea, eb, 0.08, surface.CREEP_DREF, 20)
    assert abs(net.sum()) < 1e-9 * max(np.abs(net).sum(), 1.0)
    assert np.all(-net <= avail + 1e-12)
    assert np.abs(net).sum() > 0


def test_creep_relaxes_a_step_toward_a_slope():
    g = build_grid(4)
    shelf, h, cover = _step(g)
    iso = np.full(g.n, 200.0)
    ea, eb = _sea_edges(g, np.ones(g.n, bool))
    net = surface._creep(h, iso, cover, ea, eb, 0.08, surface.CREEP_DREF, 30)
    h2 = h + net * iso
    # the deep cells next to the shelf gain, the shelf's edge cells lose, far cells barely change
    nb_shelf = np.add.reduceat(shelf[g.nbr_idx], g.nbr_off[:-1]) > 0
    foot = ~shelf & nb_shelf
    edge = shelf & (np.add.reduceat(~shelf[g.nbr_idx], g.nbr_off[:-1]) > 0)
    assert net[foot].min() > 0 and net[edge].max() < 0
    drop = lambda z: np.abs(z[ea] - z[eb])[shelf[ea] != shelf[eb]].mean()  # noqa: E731
    assert drop(h2) < 0.9 * drop(h)
    far = g.centers[:, 0] < -0.5
    assert np.abs(net[far]).max() < 1e-6


def test_creep_leaves_bare_rock_alone():
    g = build_grid(4)
    _, h, _ = _step(g)
    ea, eb = _sea_edges(g, np.ones(g.n, bool))
    net = surface._creep(h, np.full(g.n, 200.0), np.zeros(g.n), ea, eb, 0.08, surface.CREEP_DREF, 30)
    assert np.all(net == 0)


def test_erode_with_creep_conserves_the_column_and_moves_only_cover():
    """Through surface.erode: an all-sea world (no rivers) with a covered shelf over bare floor. The total crust
    is unchanged, no cell loses more than its cover, and the shelf's basement stays where it was."""
    g = build_grid(4)
    shelf, h, cover = _step(g)
    n = g.n
    thick = np.where(shelf, 30.0, 7.0)
    mix = np.zeros((n, len(surface.MIX_ROCKS)))
    mix[:, 4] = 0.3 * cover  # sand
    mix[:, 1] = np.where(shelf, 0.5, 0.0)  # lava flows: not movable
    args = (g, h, thick, cover, mix, np.full(n, surface.SHALE, np.uint8), shelf, np.full(n, 800.0),
            np.full(n, 300.0), np.full(n, 500.0), np.full(n, 1000.0), 2.0, Params().hillslope, 1e30, 2000.0, 0.0,
            2.0 ** (4 - 5), np.full(n, 170.0))
    t0, c0, m0, *_ = surface.erode(*args)
    t1, c1, m1, *_, crept = surface.erode(*args, slope_k=1000.0)
    assert np.allclose(t0, thick) and np.allclose(c0, cover)
    assert abs(t1.sum() - thick.sum()) < 1e-9 * thick.sum()
    assert np.all(c1 >= mix[:, 1] - 1e-12)  # the lava stays
    assert np.allclose(t1 - c1, thick - cover)  # basement untouched
    assert np.allclose(m1[:, 1], mix[:, 1])
    assert crept.sum() > 0 and np.all(crept <= cover - mix[:, 1] + 1e-12)
    assert np.all(m1[:, 4] <= mix[:, 4] + 1e-12)  # the sand leaves pro rata (and arrives as mud)
    assert np.all(m1 >= 0)
