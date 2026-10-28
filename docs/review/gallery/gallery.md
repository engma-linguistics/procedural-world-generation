# Showcase gallery (12 worlds, 2026-10-27/28)

All: `planet make --level 7 --myr 1000 --name <name> [--set ...]`, preset earthlike, 300 kyr time zoom, finished world at the time zoom's latest interglacial, highlights plus 4 regional zooms. Launched together on main at 41e9db20 (12 sims at once, load 100-200, ~5 h wall including the time zoom). No code changes. No failed runs; no tracebacks. All logs show only `RuntimeWarning: fresh water into the sea doesn't balance` (+-0.02..0.04 m/yr) from climate.py:2335.

"Finish moment" is `finish_moment` in each run.json (PW-866 finish window: the latest human-habitable moment in the run's last 10 Myr, else the run's end, flagged).
Pass = a habitable moment was found. FLAGGED = no habitable moment in the last 10 Myr (0 of 20 candidates); the world was finished at the run's end anyway and fails the listed checks.

Params available to `--set`: `planet/tectonics/params.py` (n_plates, start, continental_fraction, tilt, climate_offset, heat_start, ...). "Ocean water" has no direct knob; continental_fraction (default 0.4) is used as the land/ocean proxy.

| Name | Seed | Run | World | `--set` | Finish moment |
|---|---|---|---|---|---|
| gallery-stock-1 | 201 | a2bd9c | bdf72c | defaults | FLAGGED: 0/20 pass, end fails temperature |
| gallery-stock-2 | 202 | f46f51 | 6efe6b | defaults | FLAGGED: 0/20 pass, end fails temperature |
| gallery-stock-3 | 203 | 2b53a0 | aafda0 | defaults | passed, at 995.5 Myr (4.5 before end; 9/20 pass; end fails temperature) |
| gallery-stock-4 | 204 | 9a9cfe | 6612de | defaults | passed, at end (20/20) |
| gallery-drift-8plates | 211 | b92096 | c690e4 | n_plates=8 | passed, at end (18/20) |
| gallery-drift-16plates | 212 | 85f322 | 0b1067 | n_plates=16 | FLAGGED: 0/20 pass, end fails temperature |
| gallery-drift-scattered | 213 | 7db69a | d30c0e | start=scattered | passed, at 996.5 Myr (13/20; end fails temperature) |
| gallery-drift-wetter | 214 | 35f382 | 64f4dc | continental_fraction=0.33 | passed, at 997 Myr (13/20; end fails temperature) |
| gallery-drift-drier | 215 | 69536e | 7813a1 | continental_fraction=0.47 | FLAGGED: 0/20 pass, end fails temperature and land ice |
| gallery-drift-tilt16 | 216 | 1ed273 | 7fe71e | tilt=16 | passed, at end (20/20) |
| gallery-edge-wet | 221 | 0f316f | 3c73f9 | continental_fraction=0.22 | FLAGGED: 0/20 pass, end fails temperature and land ice |
| gallery-edge-28plates | 222 | 54da15 | ae95b2 | n_plates=28 | FLAGGED: 0/20 pass, end fails temperature and land ice |

Other ids (time zoom; regional zooms):
- stock-1: tz b20a87; zooms 7f1c23 df8ee9 3a8251 cdc737
- stock-2: tz d2bf79; zooms 155837 f9d7b4 2a7e22 6ea0c0
- stock-3: tz a590c5; zooms d83517 765a44 596603 17de29
- stock-4: tz ee7fff; zooms 4eed6d 983458 7b5e9a fa4b68
- drift-8plates: tz 1df15c; zooms 3f5416 50e6dd 0df64a f90c0a
- drift-16plates: tz 8f0d8a; zooms a54874 af55f1 770859 9d56c5
- drift-scattered: tz 5bfe8f; zooms 8ceeb4 cc2380 a46ece bb835d
- drift-wetter: tz 5c64b6; zooms e214d8 f69cf1 ddb08a 94f2a7
- drift-drier: tz f14da9; zooms c6c08f 7e7182 6b5b13 31247b
- drift-tilt16: tz ca3b96; zooms 72d70e ec2eba 63ef69 5fb71f
- edge-wet: tz d4a95c; zooms 423427 cf3dcb 792e68 c1f613
- edge-28plates: tz e13123; zooms 1ec2f0 75fc00 6e234f 6e53d2

Notes
- 6 of 12 flagged, including 2 of 4 stock seeds (all fail temperature at run end), so the flag is not specific to the nudged params. Kept as made; no retries with other seeds.
- Both edge worlds are flagged and also fail land ice. The "edge" values (continental_fraction=0.22, n_plates=28) may be past the livable edge; no dry edge world was made (drift-drier at 0.47 is flagged already).
- Open in the viewer: http://127.0.0.1:8765/viewer/?world=<world id>.json
