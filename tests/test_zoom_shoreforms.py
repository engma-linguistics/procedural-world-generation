"""zoom.shoreforms (PW-621): the tidal flats' D8 channels and the layer's spec/legend."""
import numpy as np

from planet.zoom import coast as ZC
from planet.zoom import shoreforms as SF


def test_flat_channels_gather_toward_the_sea():
    # a flat sloping down to the east (col), with a gentle valley along the middle row: the ebb gathers there
    ny, nx = 21, 30
    r, c = np.mgrid[0:ny, 0:nx]
    bed = -0.1 * c + 0.05 * np.abs(r - 10)
    flat = np.ones((ny, nx), bool)
    ch = SF._d8_channels(bed, flat, np.zeros_like(bed), 1.0, 20.0)
    assert ch[10, nx - 2] and not ch[0, 5]
    assert ch.sum() < flat.sum() / 3


def test_box_mean():
    a = np.zeros((9, 9))
    a[4, 4] = 9.0
    b = SF._box(a, 1)
    assert np.isclose(b[4, 4], 1.0) and np.isclose(b[3, 3], 1.0) and b[0, 0] == 0


def test_spec_and_legend():
    assert "shore_form" in ZC.LAYER_SPECS
    assert [e["id"] for e in SF.LEGEND] == [0, SF.SPIT, SF.RIDGES, SF.CHANNEL, SF.FLAT, SF.DROWNED]
