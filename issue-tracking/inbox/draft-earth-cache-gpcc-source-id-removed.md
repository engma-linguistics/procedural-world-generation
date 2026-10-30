---
title: "Earth check: GPCC reference switched from the v2018 long-term mean to v2020 1981-2010 (old source removed upstream)"
type: task
status: done
parent: null
milestone: v1
subsystem: infra
effort: s
impact: med
found_by: lane28
blocked_by: []
relates: [PW-998]
refs: [tools/earth_data.py, tools/earth_check.py]
---

## Description
In plain words. The Earth check compares the model's rain on Earth's land with GPCC, a
gridded record of rain gauges. tools/earth_data.py used to fetch GPCC's v2018 long-term
monthly means by an ERDDAP dataset id (noaa_psl_7959_51e3_b7dd). On 2026-10-30 that id
returned 404 on all three ERDDAP mirrors, and ERDDAP cut every request for the monthly
series short. So a fresh checkout, or a rebuilt cache, couldn't build the Earth caches.
(Lane 28 found this while rebuilding the main checkout's data/earth, which it had deleted
by mistake through a symlink.)

What changed (lane 28b): raw_gpcc now comes from NOAA PSL's THREDDS server. The source is
GPCC Full Data Reanalysis v2020, 1.0 deg monthly totals 1891-2019
(`Datasets/gpcc/full_v2020/precip.mon.total.1x1.v2020.nc`), and each calendar month is
averaged over GPCC_YEARS = 1981-2010, a standard 30-year normal. The data is fetched in
5-year requests with retries, because PSL rate-limits (429) and cuts responses short. The
30 years of months are cached in data/earth/raw_gpcc_monthly.npz, so a later rebuild needs
no download. v2018 is no longer on THREDDS. PSL's new full_v2025 long-term-mean file
(created 2026-10-21) held only fill values on 10-30, so it can't be used.

This is a change of reference, not of the model. No period of v2020 reproduces the old
v2018 numbers exactly. The table scores earth_check L6's GPCC land lines (excl.
Antarctica, mm/yr) for each window, against the old v2018 long-term mean as lane 27
recorded it:

| GPCC source | land mean | p10 | median | p90 | summer share |
|---|---|---|---|---|---|
| v2018 long-term mean (old, lane 27) | 790.56 | 110.33 | 546.25 | 1808.28 | 0.6538 |
| **v2020 1981-2010 (chosen)** | **789.07** | **110.28** | **546.48** | **1792.25** | **0.6537** |
| v2020 1961-1990 | 788.09 | 110.51 | 542.20 | 1800.53 | 0.6538 |
| v2020 1971-2000 | 790.05 | 112.29 | 545.42 | 1802.71 | 0.6527 |
| v2020 1991-2019 | 791.75 | 110.87 | 552.13 | 1776.83 | 0.6556 |
| v2020 1951-2000 | 788.89 | 112.66 | 540.40 | 1792.98 | 0.6526 |
| v2020 1891-2016 | 786.65 | 111.79 | 532.25 | 1793.74 | 0.6547 |

(1981-2016 was also tried: 789.65 / 111.37 / 548.72 / 1794.02 / 0.6545.)

1981-2010 is closest on the median and p10. Its land mean is 0.2% lower and its wettest
tenth 0.9% lower. Every window keeps the same 10815 cells, so the gap is the data version,
not the period or the missing-cell rule. (A first version of this table was wrong: the
scratch downloader had silently re-saved the previous 5-year chunk when a request failed.
The committed code raises instead, and the table above uses a re-checked download whose
1981-2010 months are identical to the committed code's own fetch.)

Does any earth_check pass/fail flip from the reference alone? I scored the same code
(3a58e00d, pre-PW-1050) on the old and the new reference; the model numbers are bit-identical
at L6 and L7. Nothing flips. The auto-ranked "largest systematic errors" keep the same
entries (49 at L6, 46 at L7), and the only rank swaps are outside the 20 printed (L6:
Arabia/NE Brazil at 22-23, Tibet/Patagonia at 37-38; L7: Arabia, SE USA and NE Brazil at
20-22). The point table, the Koppen scores and the cloud checks don't use GPCC. Below that,
only the observed-rain diagnostics move: the band P_obs values (under 0.9%, except 80-90 N
at +2.9%, +5 mm); the region values (up to -2.6%); single stations' P_obs (up to -6%, one
point 813 to 765 mm); the runoff ratio with GPCC rain
(0.374 to 0.373); and at L6 the Dead Sea's salt-pan cell under GPCC rain (1 to 0).

The main checkout's data/earth is rebuilt from it (real files, no links), and it also keeps
the raws that no longer download reliably:
- raw_etopo_*.npz, raw_kottek.npz plus the Wayback copy of the Kottek zip
  (Koeppen-Geiger-ASCII_wayback.zip);
- the GFED zip and raw_gfed_ba.npz;
- raw_gpcc_monthly.npz (1981-2010) and the whole v2020 series,
  raw_gpcc_v2020_monthly_1891_2019.npz (86 MB).

- [x] raster("gpcc") built from v2020 monthly totals over 1981-2010, from PSL THREDDS, with retries
- [x] the source switch and the period table recorded here and in earth_data.py's header
- [x] the model's own Earth fields unchanged (earth_check on 3a58e00d gives bit-identical model numbers on the old and the new reference)
- [x] no earth_check pass/fail flips from the reference change alone (L6 and L7)
- [x] the main checkout's data/earth rebuilt, with the raws kept
