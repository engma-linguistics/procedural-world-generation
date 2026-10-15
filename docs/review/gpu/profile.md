# GPU backend exploration (PW-249), part 1: where the time goes, and what a GPU could buy

2026-10-15, branch `worktree-agent-a893bda944cf4686c`. Machine: Threadripper 9960X (24C/48T),
RTX PRO 6000 Blackwell 96 GB (188 SMs, CUDA 13.2 driver), numba 0.68 with the TBB layer.

**Short answer.** The climate stages (atmosphere, ocean, ice mass balance, vegetation) are
~55% of a run and of a time zoom, ~52-54% of a zoom; everything else is sequential or
single-threaded numpy glue. The biggest single item, `timezoom_kernels.climate_step`, is compiled
**serial**: making it `prange` on the CPU gives 13-16x on that kernel (bit-identical) and ~2x on a
regional zoom. A GPU adds 8-16x on the climate's iterative graph kernels (`_rain` prototype:
11.4x at L7, 16x at L8, including copies), but by Amdahl that is only **~1.15-1.2x more** on a
run after the CPU fixes (~1.45x in total), ~1.25-1.5x more on a time zoom, and nothing on a zoom. Porting the whole
climate to the device would reach ~1.9-2x on a run, with ~2.3x the hard ceiling. Recommendation:
**no GPU path for now**; do the CPU fixes first (drafts under PW-247), revisit for L8. If a GPU
path is ever built: numba-cuda, fp64, persistent kernels, its own goldens. The CPU-only headroom is
~2x (section 8).

## 1. Method and caveats

- **Load.** The coordinating session ran benchmarks and an L7 showcase at the same time:
  1-, 5-, 15-min load averages between 7 and 49 during these measurements (noted per table).
  Absolute times are noisy (the same L6 500 Myr run took 231 s and 189 s); shares and per-kernel
  timings are steadier. I used **`NUMBA_NUM_THREADS=16`** throughout (one short 48-thread check).
- **Python.** First pass on Python 3.11 / numpy 2.4.6; main moved to **Python 3.14 / numpy 2.5.4**
  mid-task, so every stage table below was **re-measured on 3.14** (the GPU prototypes' CPU
  reference kernels ran in a 3.11 scratch venv with the same numba 0.68; numba kernel times don't
  depend on the Python version). The two passes agree within the load noise (L6 run shares within
  ~2 points).
- **Scripts** are in `docs/review/gpu/scripts/` (reference only, not part of `planet/`;
  `env.py` points `PLANET_DATA` at `$PROF_SCRATCH/data`). Profiles: `run_sim.py LEVEL MYR out.json`,
  `run_misc.py out.json slice|zoom|timezoom ...`, read with `stages.py`, `tree.py`, `kclass.py`,
  `glue.py`, `amdahl.py`; py-spy output with `spy.py`; GPU prototypes `gpu_climate_step.py`,
  `gpu_rain.py`, `gpu_rain_coop.py` on inputs captured by `capture.py` / `capture_fresh.py`
  (run in a separate venv with numba-cuda / CuPy).
- **Timers.** The harness (`scripts/timers.py`) wraps every planet
  Python function and method, and every numba dispatcher that isn't itself called from jitted
  code, in a stack-based `perf_counter` timer (~830k wrapped calls in a 500 Myr L6 run, ~1-2 s of
  overhead, <1%). Exclusive time is attributed to the innermost "stage root" on the call path
  (`earth.ice_sheets` -> ice, `ocean.solve` -> ocean, `hydrology.lakes` -> lakes, etc.). Kernels
  called only from other kernels can't be wrapped; `priority_flood_to` and `accumulate_lakes`
  therefore show up as exclusive time of `hydrology.route` (~2 s per 100 Myr at L6, ~11 s at L7).
- **cProfile** (3.11) confirms the per-kernel totals (it sees numba dispatchers as calls).
  On 3.14 cProfile slows the run ~5x (73 s for 20 L6 steps instead of ~15 s), so only its call
  counts are used from 3.14. **py-spy** `--native` (main thread) splits the non-kernel time into
  numpy / interpreter / libc.
- Runs: seed 3199, default params, dt 2 Myr, checkpoints every 100 Myr. L6 500 Myr (run 6a8269),
  L7 100 Myr (run on 3.14), L6 slice at 440 Myr (40 Myr replay), zooms of that world at
  1000 km / 2 km (500x500 px) and 1000 km / 1 km (1000x1000 px), time zooms L6 200 kyr at 440 Myr
  and L7 50 kyr at 100 Myr. All created under a scratch `PLANET_DATA` and deleted afterwards.

## 2. Stage shares (Python 3.14, 16 threads)

Exclusive time per stage, share of wall time.

| Stage | L6 run, 500 Myr (192.7 s, load 13-21) | L7 run, 100 Myr (189.4 s, load 15-17) |
|---|---|---|
| climate: atmosphere (`climate.compute` minus ocean) | 25.6% | 30.5% |
| ice (`earth.ice_sheets` -> `icemass.balance` -> `climate_step`) | 14.7% | 13.8% |
| ocean (`ocean.solve`, `ocean.freshwater`) | 11.5% | 6.2% |
| vegetation (`earth.update_vegetation`) | 4.9% | 5.8% |
| **climate stages together** | **56.7%** | **56.4%** |
| tectonics (plates, resolve, boundaries, crust, events, mantle, volcanoes) | 21.0% | 17.9% |
| lakes / priority flood (`hydrology.lakes`) | 7.2% | 7.9% |
| erosion / flow routing (`surface.erode` rest, `hydrology.route`) | 6.3% | 8.5% |
| isostasy | 2.0% | 2.1% |
| output (snapshot, keyframe encoding, checkpoints) | 5.4% | 4.2% |
| setup (grid, mantle basis, initial state) | 0.6% | 2.5% |
| sediment, burial, reefs; other glue | 0.7% | 0.6% |
| *top-level numba kernels, all stages* | *47.7%* | *54.4%* |

The climate update runs every `climate_every` = 4 Myr (every other step) and costs ~0.87 s (L6) /
~4 s (L7) per update; a step without it costs ~0.2 s (L6) / ~1 s (L7).

Other jobs (3.14, 16 threads):

| Job | Wall | Where it goes |
|---|---|---|
| slice L6 at 440 Myr | 18.5 s | replay of 40 Myr 85% (same mix as the run), `world.finish` 12% (climate.compute x2, waves, vegetation), checkpoint load 2% |
| zoom L6, 1000 km @ 2 km (500x500) | 11.0 s | glaciers (`icemass.balance` -> `climate_step`) **52%**, zoom vegetation 21%, `flood_d8` 6%, satellite 4% |
| zoom L6, 1000 km @ 1 km (1000x1000) | 40.9 s | glaciers **54%** (36 serial `climate_step` calls, 0.61 s each), vegetation 20%, `flood_d8` 8%, satellite 5% |
| time zoom L6, 200 kyr | 31.8 s | climate.compute (every 10 kyr) 36%, `sia_flow` 28% (lots of ice in this run; 4% in the 3.11 run's time zoom), `climate_step` 15%, `_coarse_smooth` (sheet cover, smooth_big) 13% |
| time zoom L7, 50 kyr | 27.7 s | climate.compute 57%, `climate_step` 18%, sheet cover + smoothing 8%, koppen 4% |

## 3. Top kernels (Python 3.14, 16 threads)

Inclusive time over all call sites. P = `parallel=True`, S = serial.

| Kernel | | L6 run (% of wall, ms/call) | L7 run | Zoom 1 km | Time zoom L6 / L7 | Nature |
|---|---|---|---|---|---|---|
| `timezoom_kernels.climate_step` | S | 13.7%, 12 ms | 13.1%, 51 ms | 53.8%, 611 ms | 14.9% / 17.9% | independent per cell: **data-parallel, not prange'd** |
| `climate._rain` | P | 4.5%, 68 ms | 5.8%, 409 ms | - | 4.9% / 9.2% | iterative graph stencil (160-520 iterations x 2 seasons x 2 passes) |
| `climate._stommel` | S | 2.8%, 43 ms | 5.2%, 366 ms | - | 2.9% / 7.9% | SOR in a fixed east-to-west order: **sequential by design** |
| `climate._smooth` | P | 3.5%, 1.2 ms | 4.8%, 7.5 ms | - | 4.4% / 9.6% | Jacobi stencil |
| `climate._coarse_smooth` | S | 4.4%, 3 ms | 3.5%, 7 ms | - | 13.1% / 9.1% | scatter to coarse grid, small blur, gather back: **gather part data-parallel** |
| `climate._relax_along` | P | 2.5%, 4.9 ms | 3.2%, 31 ms | - | 2.8% / 5.4% | Jacobi along flow |
| `kernels.lakes` | S | 3.5%, 3.4 ms | 3.9%, 19 ms | - | - | union-find / lake filling: sequential |
| `kernels.priority_flood` (+ `priority_flood_to` inside `hydrology.route`) | S | 2.1% (+~5%) | 2.5% (+~6%) | (`flood_d8` 7.7%) | 0.6% | heap order: sequential |
| `kernels.fill_shallow` | S | 1.4% | 1.5% | - | - | sequential |
| `ocean._relax_from` | S | 1.8% | 0.4% | - | 1.8% | Jacobi on the ocean's coarse grid (serial on purpose: small n) |
| `kernels.locate` | P | 1.3% | 2.4% | - | - | per point walk |
| `plate_kernels.resolve` / `cleanup_ghosts` | S | 1.7% | 3.0% | - | - | plate ownership bookkeeping (per plate loops) |
| `timezoom_kernels.sia_flow` | S | - | - | - | 28.2% / <1% | explicit sub-steps, per cell: data-parallel with a gather |
| `vegetation._potential`, `_step` | P | 1.4% | 1.4% | 8.1% | - | per cell |

Kernels by parallel flag, per 100 Myr: L6 parallel 5.3 s, serial 13.0 s (+~2 s nested in
`route`); L7 parallel 34.6 s, serial 68.5 s (+~11 s). So **two thirds of the kernel time runs on
one core**, half of that in kernels that could run in parallel.

## 4. GPU suitability of the hot spots

| Hot spot | Data-parallel? | Size per call | Host<->device traffic | Verdict |
|---|---|---|---|---|
| `climate_step` (ice mass balance) | yes, independent per cell | 41k-655k cells, 1M px in a 1 km zoom | ~25 arrays in, 6 out per call; called 18x per climate update, 36x per zoom | **CPU first**: prange gives 13-16x. On the GPU 7-10x faster than prange when resident, but with per-call copies it only ties prange (L7 3.6 ms vs 3.3 ms). Go only if the whole ice/climate loop lives on the device. |
| `_rain` and the graph stencils (`_smooth`, `_relax_along`, `_relax_from`, `_coarse_smooth`'s blur) | yes (Jacobi-type sweeps, gathers along CSR neighbour lists) | 164k cells at L7, hundreds of iterations | inputs once, outputs once per call; all iterations stay on the device | **Go (if any GPU work is done)**. Measured 7.8x (L6) / 11.4x (L7) / 16x (L8) for `_rain` with copies. Grows with level (iterations ~ 2^level). |
| `_stommel` (wind-driven gyres) | no: Gauss-Seidel/SOR, the sweep order is the physics | - | - | **No-go as is.** A Jacobi/red-black or multigrid version would be GPU-friendly but converges differently (output change). |
| lakes, priority flood, fill_shallow, route/accumulate, `flood_d8` | no: heap order, union-find, topological order | - | - | **No-go.** Parallel priority-flood variants exist but give different tie-breaking (different rivers). |
| tectonics (resolve, boundaries, events, crust, volcanoes) | partly; mostly Python and numpy bookkeeping on small per-plate sets | - | would cross every step | **No-go.** |
| numpy glue in climate.compute (~2000 lines: seasons, winds, humidity, clouds, koppen, months) | yes, elementwise mostly | 164k-655k | only if all of it is ported (CuPy) | Only as part of a full climate port (option C below). |
| zoom vegetation, satellite | yes | 250k-1M px | once per zoom | Small (20% of a zoom, half of it numpy glue); not worth a port alone. |

Sizes for scale: L7 164k cells (1.3 MB per float64 field), L8 655k (5.2 MB); a 500x500 zoom is
250k px, 1 km zooms 1M px. A 1.3 MB copy costs ~0.1-0.3 ms; the problem at L6/L7 is less the
bandwidth than the many small calls and kernel launches.

## 5. Prototypes (scratch venv, numba-cuda 0.30.4 / CuPy 14.2 with CUDA 13 wheels)

Installed only in a scratch venv outside the repo (`uv venv` + `uv pip install numpy==2.4.6
numba==0.68.0 cupy-cuda13x numba-cuda[cu13]`); both CuPy and numba-cuda worked with the CUDA 13.2
driver out of the box (NVRTC/NVVM from the wheels). Inputs were captured from real calls
(replayed runs at L6 400 Myr and L7 100 Myr; a fresh L8 grid's first step), outputs compared with
the CPU kernel's.

### 5.1 `timezoom_kernels.climate_step` (numba-cuda, body copied verbatim, one thread per cell)

| Cells | CPU serial (as shipped) | CPU prange, 16 thr | GPU fp64, data resident | GPU fp64 incl. copies | GPU fp32 incl. copies |
|---|---|---|---|---|---|
| L6 41k | 10.1 ms | 0.78 ms (13x) | 0.20 ms | 1.5 ms | 1.4 ms |
| L7 164k | 51.6 ms | 3.3 ms (15.6x); 2.6 ms at 48 thr | 0.50 ms | 3.6 ms | 2.1 ms |
| L8 655k | 206 ms | 15.2 ms (13.5x) | 1.3 ms | 7.7 ms | 5.8 ms |
| 1M px (zoom size; L6 inputs tiled) | 261 ms | 17.3 ms (15x) | 2.5 ms | 12.9 ms | 7.5 ms |

- prange output: **bit-identical** to the serial kernel.
- GPU fp64: max abs difference 2e-14 (smb, m/yr), 1e-14 C (temperatures); bit-repeatable run to run.
- GPU fp32: temperatures within 7e-6 C, but `f_sum` flips by up to 0.17 in some cells: the
  `sw > 0` test on `half * cos(2 pi * 3/12)` (an exact zero in theory) changes sign in single
  precision. fp32 is also no faster when resident (the kernel is latency-bound, not FP64-bound),
  so **keep fp64** (the RTX PRO 6000's fp64 rate is not the bottleneck for these kernels).

### 5.2 `climate._rain` (numba-cuda, fp64)

Two versions: (a) one kernel launch per prange loop of the CPU code (2 per season per
iteration, plus a deterministic block-tree reduction for the serial sum every 10 iterations);
(b) one persistent **cooperative** kernel running all iterations with `grid.sync()` between phases.

| Level (iterations) | CPU, 16 thr | CPU, 48 thr | GPU (a), 682-2230 launches | GPU (b), one launch, best grid | of which copies in/out | Lift (b) vs CPU 16 |
|---|---|---|---|---|---|---|
| L6 41k (160) | 66 ms | - | 30 ms | 8.5 ms (188 blocks) | 2.4 ms | **7.8x** |
| L7 164k (280) | 398 ms (335 ms in a quieter moment) | 350 ms | 58 ms | 35 ms (376 blocks) | 5.9 ms | **11.4x** (9.6x vs the quieter CPU) |
| L8 655k (520) | 3.78 s | - | 231 ms | 230 ms (376 blocks) | 16 ms | **16x** |

- Outputs: max relative difference 2e-10 (sea uptake), 2e-14 (rain); not bit-identical (the
  CPU's serial sum is a block tree on the GPU), **bit-repeatable** on the device run to run.
- The CPU kernel doesn't scale beyond 16 threads (48 threads: 350 vs 335 ms): ~1100 parallel
  regions per call, memory- and sync-bound.
- At L6/L7, launch overhead dominates the multi-launch version (L7: ~1200 launches, 50 ms
  compute); the persistent kernel removes it. At L8 the two converge (compute-bound).

## 6. Amdahl estimates (16 threads, shares from section 2-3)

Scenarios, each on top of the previous:
- **A (CPU only):** `climate_step` prange (measured 13-15.6x), `_coarse_smooth` parallel gather
  (assumed 3x), fix the ocean coarse-grid / `_geom` cache thrash (assumed 90% of it saved).
- **B:** A + GPU `_rain` (measured lift per level) + GPU graph stencils `_smooth`, `_relax_along`,
  `_relax_from`, `_coarse_smooth` (assumed 4x; each call copies its field in and out).
- **C:** A + all of climate/ocean/ice/vegetation resident on the GPU (assumed 8x on that time,
  `_stommel` left on the CPU, plus ~6-50 ms of copies per climate update).
- **Bound:** the climate stages cost nothing.

| Job | Now | A (CPU) | B (A + GPU kernels) | C (A + GPU climate) | Bound |
|---|---|---|---|---|---|
| L6 run | 192.7 s | 1.25x | 1.45x | 1.97x | 2.31x |
| L7 run | 189.4 s | 1.21x | 1.43x | 1.88x | 2.29x |
| L6 time zoom 200 kyr | 31.8 s | 1.38x (+ `sia_flow` prange: ~1.8x) | 1.72x | (n/a*) | - |
| L7 time zoom 50 kyr | 27.7 s | 1.46x | 2.14x | (n/a*) | - |
| zoom 2 km | 11.0 s | 1.97x | 1.97x | 2.06x | 2.07x |
| zoom 1 km | 40.9 s | 2.02x | 2.02x | 2.15x | 2.17x |

\* The time zoom's loop (climate_step, sheet cover, sia_flow, numpy) sits outside `climate.compute`;
porting it whole would need the time zoom loop itself on the device.

So: the CPU fixes are worth about as much as the GPU on top of them, for a fraction of the cost.
The GPU's extra over A is ~1.15-1.2x on a run (B) or ~1.55x (C), ~1.25-1.5x on a time zoom, ~0 on zooms.
At L8 the GPU share grows (`_rain` is O(n^1.5): 9.5x slower from L7 to L8 on the CPU, 6.6x on the GPU).

## 7. Route and risks

- **numba-cuda** (`numba-cuda[cu13]`): the kernel bodies port almost verbatim (`prange` loop ->
  `cuda.grid(1)`), cooperative launches and shared memory are there, fp64 math (`erfc`, `exp`)
  matches the CPU to ~1e-14. Closest to the existing code; the right choice for kernel-by-kernel
  ports (option B). Wheels ~1 GB (CUDA runtime, NVVM).
- **CuPy** (`cupy-cuda13x`): the natural choice only for porting the numpy glue of `climate.compute`
  (option C): array API on the device, RawKernel/ElementwiseKernel for loops. Most code to write and
  then keep in step with every climate change.
- JAX / warp: not tried; JAX's fp64 is opt-in and its tracing model fits the iterative,
  data-dependent loops here badly; warp is fine for kernels but adds a third kernel language.
- **Determinism / goldens:** the GPU path won't be bit-identical to the CPU (reductions, FMA
  contraction, libdevice math): needs its own goldens plus a CPU-vs-GPU tolerance test.
  Run-to-run determinism on one device holds if reductions use fixed block trees (prototype: yes);
  it changes with grid size and GPU model.
- **Two code paths:** ~6 kernels for B, ~2000 lines for C, to keep in sync with ongoing climate
  work (PW-013 and friends); Linux/NVIDIA only; optional extra `procgen-world[gpu]`.
- fp32 is not an option (branch flips; no speed gain where it matters).

**Recommendation:** option A now (drafts below), no second code path yet; reconsider B when L8
runs or long time-zoom batches become routine. Decision raised as `draft-gpu-backend-decision.md`.

## 8. CPU headroom: why does a run take so long?

The coordinator's thread scan (L6, seed 1, 100 Myr, cold process): 45.7 s at 4 threads, 41.5 s at
8, 39.9 s at 16, 39.2 s at 24, 40.4 s at 48; i.e. ~99% of the wall time at 48 threads is serial.
The buckets below (16 threads; per 100 Myr; L6 from the 500 Myr run, 38.5 s per 100 Myr in the
steady state, L7 from the 100 Myr run, 189 s) show where that serial time is.

How the main thread spends an L6 run (py-spy `--native`, 100 Hz, 6192 samples; py-spy's
unwinding slows the run ~1.5x, so shares only): numpy C code **45.7%**, numba compiled code on the
main thread (serial kernels, or the main thread's own share of a parallel one) 36.7%, inside the
TBB parallel runtime 5.3%, libc (malloc/free/memcpy outside numpy) 7.7%, the Python interpreter
itself **4.4%**. L7 (60 Myr, 50 Hz, 6523 samples): numba on the main thread 45.7%, numpy 38.5%, libc 6.9%, TBB 6.8%, interpreter 2.0%.

| Bucket | L6 s / 100 Myr | L7 s / 100 Myr | What | Achievable saving, effort |
|---|---|---|---|---|
| (a) Python interpreter, per-step bookkeeping | ~1.7 (4%) | ~4 (2%) | 34k planet function calls, ~79k builtin calls per step; tiny | ~0; not worth it |
| (b) numpy calls (single-threaded) | ~15.7 (41%) | ~68 (36%) | ~22k numpy C calls + ~13k numpy wrapper calls per step (1.3k `np.clip`, 1.7k reductions, 49 `np.add.at`), plus uncounted operators making full-grid temporaries. Top: tectonics `_world_view`, `mantle.gradient`/`eddies`, `noise.fbm`, `motion.forces`; climate `month_temps`, `months`, `koppen`, `_geom`; vegetation; `landform.classify` in the snapshot | fuse the top ~10 functions into parallel numba kernels: ~40% of the bucket, L6 ~6 s, L7 ~30 s; effort l (draft-fuse-numpy-glue-into-kernels) |
| (c1) numba kernels, data-parallel but serial | ~8.6 (22%) | ~39 (21%) | `climate_step` 5.3 / 24.8, `_coarse_smooth` 1.7 / 6.6, `resolve`+`cleanup_ghosts` 0.7 / 5.5, `_spread` 0.2 / 1.7, `_relax_from` 0.7 / 0.8 (coarse grid, serial on purpose); in time zooms also `sia_flow` | prange `climate_step` (xs, bit-identical): L6 -4.9 s, L7 -23 s; `_coarse_smooth` gather (s): -1.1 / -4.4 s; `sia_flow` (s) for time zooms (draft-parallel-climate-step-and-coarse-smooth) |
| (c2) numba kernels, inherently sequential | ~6.0 (16%) | ~37 (20%) | lakes 1.3 / 7.3, priority_flood 0.8 / 4.7, fill_shallow 0.5 / 2.8, `priority_flood_to` + `accumulate_lakes` ~2 / ~11, `_stommel` 1.1 / 9.9, bfs/components/offshore ~0.3 / ~1.6 | fewer settle passes / reuse orders: 30-50% of lakes+routing (m, small output changes; draft-lakes-settle-passes); `_stommel` warm start or multigrid: -50-80% of it (m, output change; draft-stommel-solver-sequential) |
| (c3) numba kernels already parallel | 5.3 (14%) | 34.6 (18%) | `_rain`, `_smooth`, `_relax_along`, `locate`, vegetation | little on CPU: `_rain` doesn't scale past 16 threads (GPU territory) |
| (d) startup, imports, numba cache loading | ~2 per process | ~6 per process | imports 0.15 s, `build_grid` 0.15 / 0.5 s, `Simulation` init (mantle basis) 1.2 / 4.3 s, first-call cache loads ~0.3-1 s | cache mantle basis + grid on disk: -1 / -4 s per process (s; draft-startup-and-checkpoint-io) |
| (e) I/O (checkpoints, keyframes) | ~0.9 | ~3.2 | `save_checkpoint` 0.74 / 2.4 s each (1 per 100 Myr), encoding 0.06 / 0.25 s, report 0.02 / 0.5 s (snapshot compute is in (b): 1.3 / 5 s) | background-thread checkpoint writes: ~all of it (s) |
| (f) work repeated more often than needed | (in the above) | (in the above) | climate every 4 Myr = 21.9 / 107 s per 100 Myr (60% of the steps' time); ice balance = 2 calls x 9 orbit states per update; ocean coarse grid rebuilt every update + `_geom` cache eviction 1.9 / 6.4 s; `_settle` 3 passes, ~9 priority floods per step | cache fix (s, bit-identical): -1.7 / -5.8 s (draft-ocean-coarse-grid-cache-thrash). Climate every 8 Myr: ~-30% of a run but changes outputs (needs-decision: draft-climate-cadence-decision) |

Also seen: with TBB the worker threads spin while the main thread is serial: an 8.5 s cold L6
process used 79 s of user CPU (9 cores busy on average). It doesn't cost this job wall time, but it
takes cores from concurrent jobs (relevant to PW-250's concurrent-compute plan).

**Verdict.** The current runtime is **not near the floor, but the floor is ~2x away, not 5-10x**
(CPU only, outputs kept). In order:
1. `climate_step` prange (xs, bit-identical): L6 ~-13%, L7 ~-12%, **zooms ~2x**, time zooms ~-14%.
2. Ocean coarse-grid / `_geom` cache fix (s, bit-identical): ~-4-5%.
3. `_coarse_smooth` parallel gather, `sia_flow` parallel sub-steps (s): ~-2-3% on runs, ~-10-25% on time zooms.
   Items 1-3 together: **~1.25x on runs, ~2x on zooms, ~1.4-1.8x on time zooms**, within a day.
4. Fuse the numpy glue into parallel kernels (l): another ~1.2-1.3x on runs.
5. Fewer lake/route passes, `_stommel` warm start (m, small output changes): ~1.1x.
6. Async checkpoints, cached init (s): a few %.
Items 1-6: **~1.8-2x** on an L7 run (189 s per 100 Myr -> ~100 s). Beyond that only model changes
help: the climate cadence (~1.3x more, output change) or a different algorithm for the sequential
hydrology. 5x is not on the table on the CPU without changing outputs, 10x not at all; the GPU
(section 6) adds ~1.2-1.5x on top of item 1-3 at best for runs.

## 9. Follow-ups (inbox drafts)

- `draft-parallel-climate-step-and-coarse-smooth.md` (PW-247): prange `climate_step`, parallel `_coarse_smooth` and `sia_flow`.
- `draft-ocean-coarse-grid-cache-thrash.md` (PW-247): cache the ocean's coarse grid; stop evicting `_geom`.
- `draft-fuse-numpy-glue-into-kernels.md` (PW-247): the single-threaded numpy bucket.
- `draft-lakes-settle-passes.md` (PW-247): fewer sequential flood/route passes.
- `draft-stommel-solver-sequential.md` (PW-247): faster gyre solver.
- `draft-startup-and-checkpoint-io.md` (PW-247): init caching, async checkpoints.
- `draft-climate-cadence-decision.md` (needs-decision, PW-247): climate every 8 Myr?
- `draft-gpu-backend-decision.md` (needs-decision): GPU path or not, and which backend.
- `draft-gpu-port-climate-stencils.md`: the GPU port, only if the decision says B.
