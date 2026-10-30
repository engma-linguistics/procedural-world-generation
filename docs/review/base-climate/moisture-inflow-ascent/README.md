# Lane 62: inflow depth (PW-1099) and convergence ascent (PW-1100), parked as a patch

`moisture-inflow-ascent.patch` (against 5bd36595) adds `climate.inflow_share`, `climate.convergence`, the ascent
term, TUNE `inflow_bl` / `ascent` (both off) and their tests. To apply it, run `git apply` on the patch from the repo
root. The numbers, and why it is parked, are in PW-1099's and PW-1100's Updates.
