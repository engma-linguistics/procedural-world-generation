# Languages

*Last updated 2026-11-11 (after lane 20). Each page here has a short part for Daniel on top and a longer part for agents below the line.*

## What it is

A pass over a finished peoples run. It grows every people's languages over the last 20,000 years, in half-millennium steps, using real-world statistics rather than hand-made languages. It produces:

- sounds, sound change, words with etymologies, and grammar;
- splits, contact and language shift;
- names for peoples, places, rivers, gods and persons;
- the Common, rendered as English;
- glossed sentences, a fable, recipes, and audio.

## How to look at it

- **Viewer:** `uv run python -m planet langserve a24559` opens http://127.0.0.1:8790/.
- **Pages:**
  - [demo](https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs): ten languages, with sentences, the fable and audio;
  - [sisters](https://claude.ai/artifact/YD1V4gaWYbqaontwgb37B9): related languages side by side;
  - [places](https://claude.ai/artifact/4UWoSY3i1jqkz9zYzY1gVA): place names;
  - [Language Desk](https://claude.ai/artifact/HYNL244a8zVvfSGFWK5Fgw): open questions for you.
- **Finding a language by description** ("something like Sindarin"): ask for it. The `language-finder` skill does the search.

## Where it stands

- `planet make` runs the language pass by default. It takes about 10 minutes on a24559.
- That run has 626 living varieties, grouped into 581 named languages.
- 16 of 17 realism checks pass. The one that fails, how far back scholars can trace families, you accepted.
- Next: a short finish line (epic PW-1736, about two weeks), then the language work is done. See [what's open](status.md).

More: [how it works](how-it-works.md), [what's open](status.md).

---

## For agents

### Pages in this folder
| Page | Holds |
|---|---|
| this page | entry point, commands, artifacts, coordinator recipe |
| [how-it-works.md](how-it-works.md) | pipeline, module map, data tables, output files, determinism |
| [status.md](status.md) | checks with current values, open tickets grouped, known weaknesses, what's settled |

The deep design references are linked rather than copied:
- **Build contract:** `docs/review/language/architecture.md`, sections 1–14.
- **Inputs read from the peoples run:** `docs/review/language/inputs.md`.
- **Lane-by-lane change log written for Daniel:** `docs/review/language/for-daniel.md`, about 1,900 lines with one section per lane.
- **Topic gap reviews:** `docs/review/language/*-gaps.md`.

### Commands
```
uv run python -m planet languages a24559 --workers 8            # rebuild in place (~10 min). Only the coordinator writes runs/a24559.
uv run python -m planet languages a24559 --workers 8 --out DIR  # lanes: write to scratch
uv run python -m planet langserve a24559 --port 8790 [--languages FILE] [--host 0.0.0.0]
uv run python tools/language/demo_page.py runs/a24559/languages.json --out F.html --n 10 --backend espeak
uv run python tools/language/sisters_page.py runs/a24559/languages.json --before OLD.json --out F.html
uv run python tools/language/places_page.py runs/a24559/languages.json F.html
uv run python -I tools/language/real_inventory.py --check        # real-language benchmark, ~50 s (PW-1641)
uv run python tools/language/find.py ...                         # finder; see the language-finder skill
uv run pytest -q tests/test_language_*.py tests/test_languages_viewer.py
```

### Runs
- **Main language run:** a24559, the old Earth-like B peoples run, kept because Daniel reads it. It writes `runs/a24559/`:
  - `languages.json` (~65 MB);
  - `languages-etym.json` (~65 MB);
  - `languages-snapshots.json` (~28 MB).
- **Second test world:** de1cc6. It has a baseline in the lane scratch folders.
- **Seven Meals:** a stress tree only; frozen per the owner on 11-04.

### Artifacts
| Artifact | URL | Built by |
|---|---|---|
| Demo (v24) | https://claude.ai/artifact/GQUxhWHnErqn3zx7MTaFUs | `tools/language/demo_page.py --backend espeak` (always eSpeak) |
| Sisters (v5) | https://claude.ai/artifact/YD1V4gaWYbqaontwgb37B9 | `tools/language/sisters_page.py`; needs a pre-lane-15 `--before` copy |
| Places (v4) | https://claude.ai/artifact/4UWoSY3i1jqkz9zYzY1gVA | `tools/language/places_page.py` |
| Language Desk | https://claude.ai/artifact/HYNL244a8zVvfSGFWK5Fgw | source `docs/review/language/desk/index.html`; answers in db collection `answers` |
| Real-inventory experiment | https://claude.ai/artifact/D9zoxQnya6RG5uYspUJX84 | `tools/language/real_inventory.py --html` |
| Original design doc | https://claude.ai/artifact/58m5qxKajjfn6TkTqq3EL2 | (the *what*; architecture.md is the *how*) |

### Coordinator recipe for a language lane
1. Brief from main in a worktree. The lane writes language output only with `--out` to scratch. It stays at 8 cores or fewer and leaves `runs/a24559` alone.
2. When the lane reports, merge it into the `lang-lane` worktree (`.claude/worktrees/lang-lane`) with `--no-ff`. Run the full suite there (`pytest -q -x -n 8`, about 26 min), then `git merge --ff-only lang-lane` from main.
3. Rebuild a24559 in place. Republish the demo, sisters and places pages, then restart langserve. Update this folder, `decisions.md` and the lane's for-daniel.md section.
4. Live owner rulings: [decisions.md](../decisions.md), as dated lines under "Peoples, culture, culinary" (search "language" or "Language Desk").
