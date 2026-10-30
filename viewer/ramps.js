// Colour ramps shared by the globe (globe/layers.js) and the regional zoom (zoom.html), and the lightness check
// behind the ?ramps=new preview (PW-1027; a taste call for the owner, not a default).
// A ramp is [[value, '#rrggbb'], ...]. For "how much" ramps the eye reads lightness as the amount, so a ramp that gets
// lighter and then darker again makes the lowest and the highest values look alike. ?ramps=new rebuilds every such
// ramp (not the diverging ones, the elevation tints or the categories) with the same hues, its lightness running
// evenly from its darkest to its lightest stop, in the direction the old ramp went from its first stop to its last.

// the globe's temperature, rain and soil fertility: the zoom draws with these too under ?ramps=new
export const TEMPERATURE = [[-30, '#2b3f99'], [-10, '#5b8fd6'], [0, '#e6f0f5'], [12, '#f4d27a'], [24, '#e2703a'], [32, '#9e1c1c']];
export const PRECIPITATION = [[0, '#d9c49a'], [300, '#c9c27a'], [800, '#7fb35a'], [1600, '#2f8f5a'], [2500, '#1f6f8f'], [4000, '#203f8f']];
export const FERTILITY = [[0, '#d8c8a8'], [0.25, '#c9a86a'], [0.5, '#a9b85a'], [0.75, '#5f9f3a'], [1, '#1f5f22']];

export const RAMPSET = (() => { try { return new URLSearchParams(location.search).get('ramps') || ''; } catch { return ''; } })();

// ---- sRGB <-> CIELAB (D65)
const lin = (u) => (u <= 0.04045 ? u / 12.92 : ((u + 0.055) / 1.055) ** 2.4);
const gam = (u) => (u <= 0.0031308 ? 12.92 * u : 1.055 * u ** (1 / 2.4) - 0.055);
const F = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116);
const Fi = (t) => (t ** 3 > 216 / 24389 ? t ** 3 : (116 * t - 16) / (24389 / 27));
export const hexRgb = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16));
export const rgbHex = (c) => '#' + c.map((u) => Math.round(Math.max(0, Math.min(255, u))).toString(16).padStart(2, '0')).join('');
export function lab(hex) {
  const [r, g, b] = hexRgb(hex).map((u) => lin(u / 255));
  const x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, y = 0.2126 * r + 0.7152 * g + 0.0722 * b, z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883;
  return [116 * F(y) - 16, 500 * (F(x) - F(y)), 200 * (F(y) - F(z))];
}
export function labHex([L, a, b]) {
  // (out of gamut: the chroma is pulled in until it fits, so the lightness stays what was asked for)
  for (let k = 1; k >= 0; k -= 0.05) {
    const fy = (L + 16) / 116, x = 0.95047 * Fi(fy + a * k / 500), y = Fi(fy), z = 1.08883 * Fi(fy - b * k / 200);
    const rgb = [3.2406 * x - 1.5372 * y - 0.4986 * z, -0.9689 * x + 1.8758 * y + 0.0415 * z, 0.0557 * x - 0.204 * y + 1.057 * z];
    if (k <= 0.05 || rgb.every((u) => u >= -0.001 && u <= 1.001)) return rgbHex(rgb.map((u) => 255 * gam(Math.max(0, Math.min(1, u)))));
  }
}

// ---- the lightness check
// ramps whose light middle is meant (diverging: temperature, the model-minus-observed differences, salinity, crust age,
// the wetter/drier rainfall ratio; crust thickness, blue ocean floor against green-to-red continents),
// the elevation tints (a convention) and two-colour pickers
export const EXEMPT = /temperature|dew point|salinity|crust age|crust thickness|ratio|elevation|bed under ice|minus|diff|obs|radiation|sun on slopes|wetness|^twi$|travel|plant type|^sea$|temp$/i;
export const lightness = (stops) => stops.map(([, c]) => Math.round(lab(c)[0]));
export function monotonicIn(stops, tol = 3) {
  const L = lightness(stops);
  let up = false, down = false;
  for (let i = 1; i < L.length; i++) { if (L[i] > L[i - 1] + tol) up = true; if (L[i] < L[i - 1] - tol) down = true; }
  return !(up && down);
}
// the same hues, lightness evenly from the darkest stop's to the lightest's, rising if the old ramp ended lighter than it began
export function monotonic(stops) {
  const L = lightness(stops), lo = Math.min(...L), hi = Math.max(...L), rise = L[L.length - 1] >= L[0], n = stops.length - 1;
  return stops.map(([v, c], k) => { const [, a, b] = lab(c); return [v, labHex([rise ? lo + (hi - lo) * k / n : hi - (hi - lo) * k / n, a, b])]; });
}
// ?ramps=new: rebuild, in place, every ramp of R (name -> stops) that is neither monotonic nor exempt;
// returns [name, lightness before, lightness after, stops before] for the comparison page
export function applyRampSet(R) {
  const out = [];
  for (const [k, stops] of Object.entries(R)) {
    if (!Array.isArray(stops) || EXEMPT.test(k) || monotonicIn(stops)) continue;
    const before = stops.map((s) => [...s]), next = monotonic(stops);
    stops.forEach((s, i) => { s[1] = next[i][1]; });
    out.push([k, lightness(before), lightness(stops), before]);
  }
  return out;
}
// the zoom's ramps are [value, [r, g, b]]: the same rebuild there, and the globe's temperature, rain and fertility
export function applyZoomRampSet(R, RAIN, TEMP) {
  const toRgb = (st) => st.map(([v, c]) => [v, hexRgb(c)]);
  RAIN.splice(0, RAIN.length, ...toRgb(PRECIPITATION));
  TEMP.splice(0, TEMP.length, ...toRgb(TEMPERATURE));
  if (R.soil_fertility) R.soil_fertility[0] = toRgb(FERTILITY);
  const hex = Object.fromEntries(Object.entries(R).map(([k, [st]]) => [k, st.map(([v, c]) => [v, rgbHex(c)])]));
  const changed = applyRampSet(hex);
  for (const [k] of changed) R[k][0] = toRgb(hex[k]);
  return changed;
}
