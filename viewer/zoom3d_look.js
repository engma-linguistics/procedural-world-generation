// The zoom 3D view's surfaces (zoom3d.js): glaciers, water and sky.
//
// - Terrain: the 2D layer's colours (zoom.html) as before, plus, from a data
//   texture of the zoom's heights and ice: glaciers shaded as ice (white to
//   blue with thickness, a sheen, crevasse bands across the flow where the ice
//   surface steepens, debris on the thin ice at their snouts), and the painted
//   rivers shimmering downstream (a flow texture: each river stroke's direction).
// - Sea: tinted by depth (turquoise shallows to navy deeps, clearer in the
//   shallows), foam along the shore, sun glints; only where the sea is (not on
//   land below sea level away from it).
// - Lakes: their kind's colour (fresh blue, salt pink), lighter in the shallows,
//   with glints.
// - Sky: a dome graded from a pale horizon to a deeper zenith, and haze (fog of
//   the horizon's colour) that thickens with distance.
//
// Scene units as zoom3d.js: x, z in km (z south), y in metres scaled by exag / 1000.
import * as THREE from 'three';

// value noise and fbm, shared by the shaders
const NOISE = /* glsl */ `
float z3Hash(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float z3Noise(vec2 p) {
  vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
  return mix(mix(z3Hash(i), z3Hash(i + vec2(1, 0)), u.x), mix(z3Hash(i + vec2(0, 1)), z3Hash(i + vec2(1, 1)), u.x), u.y);
}
float z3Fbm(vec2 p) { float v = 0.0, a = 0.5; for (int k = 0; k < 4; k++) { v += a * z3Noise(p); p *= 2.03; a *= 0.5; } return v; }
`;

// [1 2 1] smoothing of a nx x ny field, `passes` times (edges clamped)
function blur(a, nx, ny, passes) {
  let src = Float32Array.from(a), tmp = new Float32Array(a.length);
  for (let k = 0; k < passes; k++) {
    for (let r = 0; r < ny; r++) for (let c = 0; c < nx; c++) {
      const i = r * nx + c;
      tmp[i] = 0.25 * src[i - (c > 0)] + 0.5 * src[i] + 0.25 * src[i + (c < nx - 1)];
    }
    for (let r = 0; r < ny; r++) for (let c = 0; c < nx; c++) {
      const i = r * nx + c;
      src[i] = 0.25 * tmp[i - (r > 0) * nx] + 0.5 * tmp[i] + 0.25 * tmp[i + (r < ny - 1) * nx];
    }
  }
  return src;
}

// The zoom's heights, ice and sea as a half-float RGBA texture on the pixel
// centres' grid (the terrain's uv): R ground (m), G ice thickness (m; smoothed
// over a few pixels, so the glaciers' outlines don't show the pixels' steps),
// B 1 on sea pixels, A lake depth (m).
export function dataTexture(t) {
  const { nx, ny, L } = t, n = nx * ny, d = new Uint16Array(4 * n), h = THREE.DataUtils.toHalfFloat;
  const ice = L.ice ? blur(L.ice, nx, ny, 2) : null;
  for (let r = 0; r < ny; r++) for (let c = 0; c < nx; c++) {
    const i = r * nx + c, j = 4 * ((ny - 1 - r) * nx + c);  // (row 0 at the bottom: v = 0 is the south edge)
    d[j] = h(L.elevation[i]); d[j + 1] = h(ice ? ice[i] : 0); d[j + 2] = h(L.water[i] === 1 ? 1 : 0);
    d[j + 3] = h(L.water[i] === 2 ? L.lake_depth[i] || 0 : 0);
  }
  const tex = new THREE.DataTexture(d, nx, ny, THREE.RGBAFormat, THREE.HalfFloatType);
  tex.magFilter = tex.minFilter = THREE.LinearFilter;
  tex.needsUpdate = true;
  return tex;
}

// The rivers' flow directions, drawn with the same strokes as the colour
// texture's rivers (Tile.texture): each stroke coloured by its direction
// (r, g = east, south as 0..1; b = 1 on the river), on black.
export function flowCanvas(w, h) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const cx = cv.getContext('2d');
  cx.fillStyle = '#000'; cx.fillRect(0, 0, w, h);
  return cv;
}

const shared = { uTime: { value: 0 } };
export const time = shared.uTime;

// the uniforms the terrain, sea and lake shaders read
function dataUniforms(t, tex) {
  return { uData: { value: tex }, uTexel: { value: new THREE.Vector2(1 / t.nx, 1 / t.ny) }, uRes: { value: t.res },
           uOrigin: { value: new THREE.Vector4(t.x0, t.z0, t.w, t.d) } };
}

// ------------------------------------------------------------ terrain
// A MeshStandardMaterial (rough, as the Lambert it replaces) whose fragment
// adds the glaciers and the rivers' shimmer. look.ice: tint the ice (natural
// layers: satellite, relief, height, hillshade; elsewhere only its crevasses
// and sheen, so a categorical layer keeps its colours).
export function terrainMaterial() {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.92, metalness: 0 });
  m.userData.u = { uData: { value: null }, uFlow: { value: null }, uTexel: { value: new THREE.Vector2(1, 1) }, uRes: { value: 1 },
                   uIceTint: { value: 1 }, uFx: { value: 1 }, uTime: shared.uTime };
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, m.userData.u);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWPos;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vWPos;
uniform sampler2D uData, uFlow; uniform vec2 uTexel; uniform float uRes, uIceTint, uFx, uTime;
${NOISE}`).replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
#ifdef USE_MAP
{
  vec4 D = texture2D(uData, vMapUv);
  float ice = D.g;
  if (ice > 0.5 && uFx > 0.5) {
    // the ice surface's slope (m/m) and downhill direction (x east, z south) (the
    // ground is the ice surface: the zoom's heights include its glaciers), and
    // which way the ice thins
    vec4 E1 = texture2D(uData, vMapUv + vec2(uTexel.x, 0.0)), E0 = texture2D(uData, vMapUv - vec2(uTexel.x, 0.0));
    vec4 S1 = texture2D(uData, vMapUv - vec2(0.0, uTexel.y)), S0 = texture2D(uData, vMapUv + vec2(0.0, uTexel.y));
    vec2 g = vec2(E1.r - E0.r, S1.r - S0.r) / (2.0 * uRes * 1000.0);
    vec2 gi = vec2(E1.g - E0.g, S1.g - S0.g);
    float slope = length(g);
    vec2 dn = slope > 1e-6 ? -g / slope : vec2(0.0, 1.0);
    vec2 p = vWPos.xz;
    float along = dot(p, dn), across = dot(p, vec2(-dn.y, dn.x));
    float cover = smoothstep(2.0, 30.0, ice);  // (the margin blends in)
    // ice: white, bluer where thick; a smoother, shinier surface
    vec3 iceCol = mix(vec3(0.94, 0.97, 1.0), vec3(0.70, 0.82, 0.94), smoothstep(150.0, 1800.0, ice));
    iceCol *= 0.94 + 0.08 * z3Fbm(p * 0.9);
    diffuseColor.rgb = mix(diffuseColor.rgb, iceCol, cover * 0.75 * uIceTint);
    roughnessFactor = mix(roughnessFactor, 0.6, cover);
    // crevasses: bands across the flow, broken up, where the ice steepens (it stretches);
    // spaced to the zoom's pixels, and faded out where they'd be finer than the screen's
    float wl = max(0.3, 0.45 * uRes), ph = along / wl + 0.9 * z3Fbm(vec2(across / (2.0 * wl), along / (5.0 * wl)));
    float aa = 1.0 - smoothstep(0.25, 0.6, fwidth(ph));
    float crev = smoothstep(0.8, 0.97, sin(6.2832 * ph)) * smoothstep(0.015, 0.08, slope) * smoothstep(0.35, 0.6, z3Fbm(p / (1.5 * wl) + 7.0)) * cover * aa;
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.16, 0.30, 0.46), crev * 0.75);
    // steep ice (icefalls, the snouts' fronts) bluer
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.55, 0.72, 0.88), smoothstep(0.08, 0.3, slope) * cover * 0.5 * uIceTint);
    // the snout: where the ice thins downhill (not along its sides), grey with debris (moraine)
    float snout = max(0.0, dot(normalize(gi + 1e-5), -dn)) * (1.0 - smoothstep(10.0, 120.0, ice)) * smoothstep(0.5, 4.0, ice);
    diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.42, 0.40, 0.37) * (0.8 + 0.4 * z3Noise(p * 6.0 / uRes)), snout * 0.45);
  }
  // the rivers: highlights running downstream (direction: the flow texture's stroke colour)
  vec4 F = texture2D(uFlow, vMapUv);
  if (F.b > 0.3 && uFx > 0.5) {
    vec2 dir = normalize(F.rg / F.b * 2.0 - 1.0 + 1e-4);
    // ripples carried downstream (a flow map: noise moved along the direction in two
    // phases half a period apart, cross-faded, so it never stretches); scaled to the zoom's pixels
    vec2 q = vWPos.xz / uRes * 2.5;
    float t0 = fract(uTime * 0.3), t1 = fract(uTime * 0.3 + 0.5), wt = abs(2.0 * t0 - 1.0);
    float n = mix(z3Fbm(q - dir * t0 * 1.6), z3Fbm(q - dir * t1 * 1.6 + 3.7), wt);
    float aa = 1.0 - smoothstep(0.4, 1.2, length(fwidth(q)));
    float spark = smoothstep(0.6, 0.78, n) * smoothstep(0.4, 0.8, F.b) * aa;
    diffuseColor.rgb += spark * vec3(0.17, 0.21, 0.25);
    roughnessFactor = mix(roughnessFactor, 0.45, smoothstep(0.4, 0.8, F.b));
  }
}
#endif`);
  };
  m.customProgramCacheKey = () => 'z3d-terrain';
  return m;
}

// ------------------------------------------------------------ sea
export function seaMaterial() {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, roughness: 0.18, metalness: 0, depthWrite: false });
  m.userData.u = { uData: { value: null }, uFoam: { value: 1 }, uRes: { value: 1 }, uTime: shared.uTime };
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, m.userData.u);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vSeaUv; varying vec3 vWPos;')
      .replace('#include <uv_vertex>', '#include <uv_vertex>\nvSeaUv = uv;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec2 vSeaUv; varying vec3 vWPos;
uniform sampler2D uData; uniform float uFoam, uTime, uRes;
${NOISE}`).replace('#include <color_fragment>', `#include <color_fragment>
{
  vec4 D = texture2D(uData, vSeaUv);
  if (D.b < 0.3) discard;  // (no sea here: land below sea level, off the coast)
  float depth = max(-D.r, 0.0);
  float k = 1.0 - exp(-depth / 140.0);
  diffuseColor.rgb = mix(vec3(0.09, 0.42, 0.47), vec3(0.015, 0.075, 0.19), k);
  diffuseColor.a = mix(0.35, 0.93, smoothstep(0.0, 260.0, depth)) * smoothstep(0.3, 0.6, D.b);
  // foam along the shore (where the sea's mask fades to the land's), in bands moving in
  float sh = (1.0 - smoothstep(0.45, 0.92, D.b)) * (1.0 - smoothstep(5.0, 60.0, depth));
  vec2 q = vWPos.xz / uRes;
  float band = 0.5 + 0.5 * sin(uTime * 1.2 + D.b * 16.0 + 4.0 * z3Noise(q * 1.5));
  float foam = sh * band * smoothstep(0.3, 0.65, z3Fbm(q * 2.0 + uTime * 0.04)) * uFoam;
  diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.92, 0.95, 0.96), foam * 0.85);
  diffuseColor.a = max(diffuseColor.a, foam * 0.9);
}`).replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
  roughnessFactor = 0.12 + 0.2 * z3Fbm(vWPos.xz * 4.0 + vec2(uTime * 0.08, 0.0));`);
  };
  m.customProgramCacheKey = () => 'z3d-sea';
  return m;
}

// ------------------------------------------------------------ lakes
// (vertex colours: the kind's; lighter and greener in the shallows)
export function lakeMaterial() {
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: 0.2, metalness: 0,
    polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
  m.userData.u = { uData: { value: null }, uOrigin: { value: new THREE.Vector4(0, 0, 1, 1) }, uTime: shared.uTime };
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, m.userData.u);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nuniform vec4 uOrigin; varying vec2 vLakeUv; varying float vSurf; varying vec3 vWPos;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
vLakeUv = vec2((position.x - uOrigin.x) / uOrigin.z + 0.5, 0.5 - (position.z - uOrigin.y) / uOrigin.w);
vSurf = position.y;`)
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec2 vLakeUv; varying float vSurf; varying vec3 vWPos;
uniform sampler2D uData; uniform float uTime;
${NOISE}`).replace('#include <color_fragment>', `#include <color_fragment>
{
  float depth = max(vSurf - texture2D(uData, vLakeUv).r, 0.0);
  diffuseColor.rgb = mix(diffuseColor.rgb * vec3(1.15, 1.3, 1.05) + vec3(0.06, 0.08, 0.03), diffuseColor.rgb * 0.7, smoothstep(0.0, 60.0, depth));
}`).replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
  roughnessFactor = 0.12 + 0.25 * z3Fbm(vWPos.xz * 5.0 + vec2(0.0, uTime * 0.06));`);
  };
  m.customProgramCacheKey = () => 'z3d-lake';
  return m;
}

// points a tile's data and flow textures at the materials
export function bind(t, tex, flowTex, mats) {
  const u = dataUniforms(t, tex);
  for (const m of [mats.terrain, mats.sea, mats.lake]) if (m?.userData.u) m.userData.u.uData.value = tex;
  Object.assign(mats.terrain.userData.u, { uTexel: u.uTexel, uRes: u.uRes });
  mats.sea.userData.u.uRes.value = t.res;
  mats.terrain.userData.u.uFlow.value = flowTex;
  mats.lake.userData.u.uOrigin.value.copy(u.uOrigin.value);
}

// ------------------------------------------------------------ sky
export const HORIZON = new THREE.Color(0xc4d3e2), ZENITH = new THREE.Color(0x5f8fc4);
export function skyDome() {
  const m = new THREE.ShaderMaterial({
    uniforms: { uH: { value: HORIZON.clone() }, uZ: { value: ZENITH.clone() }, uG: { value: HORIZON.clone().multiplyScalar(0.92) } },
    vertexShader: 'varying vec3 vD; void main() { vD = position; vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0); gl_Position = p.xyww; }',
    fragmentShader: `varying vec3 vD; uniform vec3 uH, uZ, uG;
      void main() { float y = normalize(vD).y;
        vec3 c = y > 0.0 ? mix(uH, uZ, pow(y, 0.55)) : mix(uH, uG, min(-y * 4.0, 1.0));
        gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
      }`,
    side: THREE.BackSide, depthWrite: false, depthTest: false, fog: false,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), m);
  dome.renderOrder = -10; dome.frustumCulled = false;
  dome.raycast = () => {};
  return dome;
}
