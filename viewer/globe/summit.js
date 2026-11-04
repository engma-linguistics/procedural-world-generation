// Summit height of a cell (PW-846): the cell's mean height plus Earth's measured sub-cell relief, by the
// land relief around the cell. Display only. The same table and rule as planet/summit.py (RELIEF_KNOTS;
// tests/test_summit.py checks they match).
import { S } from './state.js';

const RELIEF_KNOTS = [
  [0, 0], [58, 86], [142, 186], [282, 464], [484, 771], [690, 950], [884, 1088],
  [1117, 1255], [1464, 1513], [1904, 1774], [2527, 2137], [3345, 2479],
];

// Summit height (m) of land cell i, or null for sea
export function summitAt(i) {
  const e = S.V.layers.elevation;
  if (!(e[i] > 0)) return null;
  let hi = e[i], lo = e[i];
  for (const j of S.V.grid.nbr[i]) if (e[j] > 0) { if (e[j] > hi) hi = e[j]; if (e[j] < lo) lo = e[j]; }
  const rel = hi - lo, K = RELIEF_KNOTS;
  let d = K[K.length - 1][1];
  if (rel < K[K.length - 1][0]) {
    let k = 1;
    while (K[k][0] < rel) k++;
    d = K[k - 1][1] + (K[k][1] - K[k - 1][1]) * (rel - K[k - 1][0]) / (K[k][0] - K[k - 1][0]);
  }
  return e[i] + d;
}

// "7,600 m summit, cell average 5,700 m" for the cell readout
export function heightText(i) {
  const s = summitAt(i), e = S.V.layers.elevation[i];
  return s == null ? `${e} m` : `summit about ${Math.round(s / 100) * 100} m (cell average ${e} m)`;
}
