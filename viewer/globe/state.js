// The globe viewer's shared state. Everything one module sets and another reads lives here; a module's own
// working state stays in that module. The rest of what the modules share is functions and constant tables.

// The view's choices: colour layer, mode, season, the picked plant type, resource, tech... (many set from the URL).
export const state = { mode: 'globe', layer: 'biome', playing: false };

// The flat map's projection (PW-838: the flat map opens in Equal Earth; equirectangular is the live three.js map,
// ?proj=equirect).
export const proj = { on: false, name: 'equal-earth', lat: 0, lon: 0, ext: null, grid: null };

export const S = {
  // V is "what we're looking at": a static world or one frame of a tectonic run.
  // Both expose V.layers (arrays indexed by cell) so colouring code is shared.
  V: null,
  mesh: null,           // the globe (or map) mesh, and its topology (geometry.js)
  topo: null,
  meshDeferred: false,  // the mesh is left out of date while the flat map's canvas covers it (geometry.js paint)
  overlays: {},         // the overlay objects by name (overlays.js)
  lastColors: null,     // the current layer's colours (paint), for the 2D map
  seaShell: null,       // the 3D relief's sea surface (one per view mode, kept across frames)
  lmEdit: -1,           // the landmass whose name is being edited (panel.js)
  tzJob: null,          // the glacial time zoom job being made, and its span (timezoom.js)
  tzKyr: 300,
  IDX: { runs: [], worlds: [], zooms: [] },  // the run / world / zoom indexes
  FAVS: new Set(),      // "run:<dir>" / "world:<id>" the owner starred (GET /api/favourites; kept by the server, not the browser)
  detailCell: -1,       // the cell the "More detail" panel shows
  hovered: -1,          // the cell under the pointer, and the info box's html for it
  infoHtml: null,
  picked: null,         // the cell picked for a regional zoom, and the zoom's size (km)
  zoomSize: 1000,
  navUi: null,          // the world navigator (navigator.js)
  lastAdvance: 0,       // when the replay last stepped a frame (playback.js, main.js's render loop)
};
