import * as THREE from 'three';
// Drawing helpers shared by the overlays.

// A text label as a sprite: the text centred at (w / 2, y) on a w x h canvas, bold, outlined (line, stroke) and filled
// with color. mat: more SpriteMaterial options; order: renderOrder; scale: [x, y] (the sprite's size on the globe).
// The overlays are rebuilt on every paint (each frame of a replay), so the drawn text is kept (PW-1045): one material
// and texture per text, colour and style, marked shared so disposeObj leaves them; only the Sprite is new each time.
const SPRITE_MATS = new Map(), SPRITE_MAX = 3000;
export function canvasSprite(text, color, { w = 256, h = 64, px = 36, line = 6, stroke = '#0b0f17', join = null, y = 34, mat = {}, order = null, scale = null } = {}) {
  const key = JSON.stringify([text, color, w, h, px, line, stroke, join, y, mat]);
  let m = SPRITE_MATS.get(key);
  if (!m) {
    if (SPRITE_MATS.size >= SPRITE_MAX) {  // (never in practice: a few hundred labels; keeps a long session bounded)
      for (const old of SPRITE_MATS.values()) { old.map.dispose(); old.dispose(); }
      SPRITE_MATS.clear();
    }
    const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
    const g = cv.getContext('2d');
    g.font = `bold ${px}px -apple-system, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = line; if (join) g.lineJoin = join; g.strokeStyle = stroke; g.strokeText(text, w / 2, y);
    g.fillStyle = color; g.fillText(text, w / 2, y);
    const tex = new THREE.CanvasTexture(cv);
    tex.userData.shared = true;
    m = new THREE.SpriteMaterial({ map: tex, ...mat });
    m.userData.shared = true;
    SPRITE_MATS.set(key, m);
  }
  const sp = new THREE.Sprite(m);
  if (order != null) sp.renderOrder = order;
  if (scale) sp.scale.set(scale[0], scale[1], 1);
  return sp;
}
