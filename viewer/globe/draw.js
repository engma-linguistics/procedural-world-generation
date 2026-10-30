import * as THREE from 'three';

// Drawing helpers shared by the overlays.

// A text label as a sprite: the text centred at (w / 2, y) on a w x h canvas, bold, outlined (line, stroke) and filled
// with color. mat: more SpriteMaterial options; order: renderOrder; scale: [x, y] (the sprite's size on the globe).
export function canvasSprite(text, color, { w = 256, h = 64, px = 36, line = 6, stroke = '#0b0f17', join = null, y = 34, mat = {}, order = null, scale = null } = {}) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d');
  g.font = `bold ${px}px -apple-system, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = line; if (join) g.lineJoin = join; g.strokeStyle = stroke; g.strokeText(text, w / 2, y);
  g.fillStyle = color; g.fillText(text, w / 2, y);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), ...mat }));
  if (order != null) sp.renderOrder = order;
  if (scale) sp.scale.set(scale[0], scale[1], 1);
  return sp;
}
