# Lineages lane: handoff 1 (2026-10-23, ~105 tool calls)

Design: `docs/proposals/lineages.md` (the stage plan, model, decisions). Code: `planet/lineages/`. Tests: `tests/test_lineages.py` (7, ~1 s, fake level-3 time zoom).

## Built
- **Stage a, recent pass** (`recent.py`, `planet recent <world|timezoom> [--kyr 30 --step 0.1 --every 0.5]`): committed 282ac61. Example run 0a04f4 (world 119973 / time zoom 1224c2, last 30 kyr).
- **Stage b/c, peoples** (`spec.py`, `habitat` in `history.py`, `spread.py` numba, `output.py`, `run.py`; `planet lineages <world> --tree dnd --tries 4`): a DAG input (TOML/JSON) with origins root / split / arrival (from outside the world, optional place) / hybrid (two parents; `contact` = only where both meet) / template (overlay on hosts, `share`, `sites`); `enabled = false` (split children re-parent; hybrids/templates of it go too); `extinct = "T"` (habitat dwindles to nothing by T; a dying side branch leaves its parent alive); `persists`; traits (flies, swims, coastal, seafaring, agricultural, nomadic, mountain, hardy, insular, cosmopolitan, subterranean); wishes (near / apart / place). Steps: run keyframes plus a step at each line's own time in deep time (connectivity-limited spread), time zoom frames (2 kyr), recent pass (100 yr, speed-limited fronts). Competition by niche overlap x kinship, late mixing from `mixing_start`, best of N tries by wish score. Output: a time-zoom-kind run, `meta.phase = 'lineages'`, layers `peoples`, `peoples_mix`, `peoples_share`, `peoples_overlay` plus terrain; meta has the tree, origins (with why: isolated part / edge / new niche / given place), centroid tracks, present summary (areas, patches, neighbours, mixing zones, wish scores), `layers/presence_present.bin` (lines x cells, %). ~20 s a try at L6.
- **Preset** `planet/lineages/samples/dnd.toml`: 37 lines (reptilian, mammalian incl. goblinoids, hominids, giant-kin; avian; elves/drow/sea elves and gnomes arriving from the feywild, tritons; half-elves, half-orcs; tieflings, aasimar, genasi templates; two extinct extras: troglodytes, elder giants) and 7 wishes. All values editable defaults.
- **Viewer**: `viewer/lineages.html` (the editor: log time axis over the three scales, drag a bar's start, edit everything per line, add custom lines / branches, enable toggles, delete, wishes, save to `<data>/lineage_trees/<name>.json`, download/upload JSON, "Run on world" and the result's origins/areas back on the bars); `index.html`: `peoples` and `peoples mix` layers on phase runs, a phase summary (time as "x kyr ago"), a peoples panel (tree with colours, times, areas; click a line to show only its range; mixing zones; wish scores; link to the editor).
- **Server** (`server.py`, additive): `GET /api/lineage-trees`, `GET|POST /api/lineage-tree?name=`, `POST /api/lineages {world, tree|raw, tries}` (synchronous under api.COMPUTE, ~20 s a try). The 8765 server needs a restart to get them.
- Screens: `docs/review/lineages/editor.png`, `globe_peoples.png` (run 992230 on world 119973, the present).

## Not done / next
1. Peoples hover row in the info box (cell's peoples and shares; needs the per-frame presence or the present bin) and origin markers / migration tracks on the globe (meta has them).
2. The editor's run blocks a server thread; move `POST /api/lineages` onto the job queue (api.any_job) with progress.
3. Family/navigator nesting of phase runs (draft lineages-store-kind).
4. Tune: mixing zones are large, island wishes failed on 119973 (draft lineages-wish-strength); episode rate (draft lineages-recent-physics).
5. An L7 showcase run and a review of the present-day maps across 3-4 seeds.
6. Overlays (templates, contact hybrids) only shown via `peoples_overlay` (no viewer layer yet).

Stored test outputs (deletable): runs 0a04f4 (recent), 57939b, 13e5f3, 992230 (peoples).
