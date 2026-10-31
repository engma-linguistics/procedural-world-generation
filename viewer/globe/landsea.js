// Land and sea, as planet/geo.py's is_land has it (PW-1229; keep the two in step: tests/test_landsea.py
// checks they agree). The sea is ground at or below sea level, not under grounded ice, that reaches the
// world ocean: its largest body of water along the grid's links, any body of SEA_MIN_KM2 or more, and any
// body one land cell of bed <= SILL_M away from one of those (a strait narrower than a cell). Ground below
// sea level cut off from it is land: a lake or a dry depression (the Dead Sea, Qattara, Death Valley).
export const SEA_MIN_KM2 = 0.3e6, SILL_M = 10;

// 1 where a cell is sea. e: m above sea level (the bed), ice: m of grounded ice (or null), nbr: each
// cell's neighbours.
export function seaMask(e, ice, nbr) {
  const n = e.length, lab = new Int32Array(n).fill(-1), q = new Int32Array(n), size = [];
  const wet = (i) => e[i] <= 0 && !(ice && ice[i] > 0);
  let k = 0;
  for (let s = 0; s < n; s++) {
    if (lab[s] >= 0 || !wet(s)) continue;
    let head = 0, tail = 1;
    q[0] = s; lab[s] = k;
    while (head < tail) {
      const i = q[head++];
      for (const j of nbr[i]) if (lab[j] < 0 && wet(j)) { lab[j] = k; q[tail++] = j; }
    }
    size.push(tail); k++;
  }
  const out = new Uint8Array(n);
  if (!k) return out;
  const cellKm2 = 4 * Math.PI * 6371 ** 2 / n;
  let big = 0;
  for (let b = 1; b < k; b++) if (size[b] > size[big]) big = b;
  const parent = Int32Array.from({ length: k }, (_, b) => b);
  const root = (x) => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
  for (let c = 0; c < n; c++) {  // (bodies one low land cell apart join)
    if (lab[c] >= 0 || !(e[c] <= SILL_M)) continue;
    let first = -1;
    for (const j of nbr[c]) {
      if (lab[j] < 0) continue;
      if (first < 0) { first = lab[j]; continue; }
      const a = root(first), b = root(lab[j]);
      if (a !== b) parent[a] = b;
    }
  }
  const seaRoot = new Uint8Array(k);
  for (let b = 0; b < k; b++) if (b === big || size[b] * cellKm2 >= SEA_MIN_KM2) seaRoot[root(b)] = 1;
  for (let i = 0; i < n; i++) if (lab[i] >= 0 && seaRoot[root(lab[i])]) out[i] = 1;
  return out;
}
