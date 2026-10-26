// Wheel zoom for an OrbitControls view, in place of its built-in one.
// three r160 divides the wheel delta by (devicePixelRatio | 0), which is 0 when the browser's page zoom
// is under 100% (Firefox at 90%: dpr 0.896), so one notch jumped straight to min or max distance.
// Same feel as zoom3d.js's wheelZoom: a notch (~100 px) is a ~10% step (owner: 2/3 of the first try), trackpads send many small ones.
export function wheelZoom(controls, canvas) {
  controls.enableZoom = false;
  canvas.addEventListener('wheel', (e) => {
    if (!controls.enabled) return;
    e.preventDefault();
    let dy = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 100 : 1);
    dy = Math.max(-120, Math.min(120, dy));
    const cam = controls.object, off = cam.position.clone().sub(controls.target);
    const d = off.length(), dNew = Math.min(controls.maxDistance, Math.max(controls.minDistance, d * Math.exp(dy * 0.0011)));
    if (d > 1e-9) cam.position.copy(controls.target).add(off.multiplyScalar(dNew / d));
    controls.update();
  }, { passive: false });
}
