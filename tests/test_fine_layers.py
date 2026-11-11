"""The fine zoom's work grid (zoom.fine_layers, PW-1679): the receivers of coarse blocks from the pixels' own channel."""

import numpy as np

from planet.zoom import fine_layers as FL
from planet.zoom import regional as Z


def test_coarse_receiver_follows_the_channel_out_of_the_block():
    n, k = 40, 4
    slot = np.full((n, n), 6, np.uint8)  # everything drains south ...
    slot[21, :] = 3  # ... to a river along row 21 that runs west
    slot[21, 0] = Z.D8_NONE
    slot[n - 1, :] = Z.D8_NONE
    area = np.ones((n, n))
    area[21, :] = 100.0 + np.arange(n)[::-1]
    rec = FL.coarse_receiver(slot, area, k, n)
    m = n // k
    assert rec.shape == (m, m)
    assert (rec[5, 1:] == 3).all()  # (the river's blocks, row 21 // 4 = 5: west)
    assert rec[5, 0] == Z.D8_NONE  # (it leaves the grid)
    assert (rec[0, :] == 6).all() and (rec[3, :] == 6).all()  # (hillslope blocks: their outlet runs south into the next block)


def test_work_factor_is_in_km():
    assert FL.work_factor(0.5, 1000) == 1 and FL.work_factor(2.0, 500) == 1
    assert FL.work_factor(0.025, 1200) == 20 and FL.work_factor(0.1, 500) == 5
