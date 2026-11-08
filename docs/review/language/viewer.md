# Languages viewer (`viewer/languages.html`)

The owner's view of a peoples run's languages (PW-986). Open `/viewer/languages.html?run=<id>` (or the **Languages** link in the
peoples workbench header). Classic scripts, no build step, house look from `theme.css`; hash routing
`#<tab>/sel=<lect>&f=<frame>&p=<people>` (plus a tab's own keys), so a view can be linked.

| File | What |
| --- | --- |
| `viewer/languages.html` | page shell, CSS, tab buttons, footer help |
| `viewer/langcore.js` | pure helpers, tested under node: `index`, `snapFull`, `stitch`, `changeLog`, `layoutTree`, `layoutDendro`, `speakUrl`, `surfaceOf`, `rootFamilies`, `intelColor`/`intelRamp`, `chainAt`, `chainBreak`, `findContinua` (the same rule as `families.continua`), `ipaPlace`/`vowelXY`, `etymChain`, `processText`, `causeText` |
| `viewer/langview.js` | run picker, loading (streamed, with progress), shared selection and frame, hash, audio buttons, lect bar, scrubber; **Families** tab |
| `viewer/langtime.js` | **A language over time** |
| `viewer/langmap.js` | **Continuum & intelligibility** |
| `viewer/langmore.js` | **Names & etymologies**, **Food words & shifts**, **Checks & voices** |
| `viewer/langgram.js` | **Grammar & sentences** (round 5) |
| `tools/language/fake_languages_json.py` | a 30-lect, 10-frame synthetic file in output.py's shape (dev and tests) |
| `tests/test_languages_viewer.py` | node tests of langcore.js, the helpers over the synthetic file, every script parses |

Screens (run a24559 with builder E's test file of 2026-11-03 22:34): `docs/review/language/screens/lang-*.png`.

## Tabs

1. **Families**: left, the true tree from `parent` links over every lect (protos, dead and living) on a 20 kyr time axis; bud solid,
   shift dashed, arrival dotted; coloured by people; dead faded; fold/unfold per node; the picked lect's line of descent bold and its
   substrate joined by a gold dotted line; the 6-10 kyr target band and the measured `horizon_kyr`. Right, the scholars' UPGMA
   (`families.scholars`) with the chance-floor and one-language cut lines, each leaf with its language swatch. People filter.
2. **Grammar & sentences** (round 5): the picked lect as spoken now. Left, its sample sentences (`sentences`), each with
   the English, the form line over the gloss line word by word (category labels in small caps), the whole sentence in IPA
   and spelling, the builder's note, and ▶ (the sentence said with phrase intonation; a yes/no question rises). Right, the
   grammar in short (`grammar_notes`): one card per topic with glossed examples, each with ▶. Below: pronouns, the words
   (the core list, or every word, with a filter), and word families seen two ways side by side, "Families a speaker
   feels" (per-word `roots`) and "Families a historian reconstructs" (per-word `etym_roots`; a file without them says
   so). The header has ▶ hear a sample and ▶ play all sentences. Dead lects show their words only; a file written before
   round 5 says to re-run the pass.
3. **A language over time**: scrubber (▶ plays 20 kyr → now). The picked lect's history through its ancestors (`stitch`): consonants
   on a place × manner grid, vowels on the trapezoid (sounds that came flash green, sounds that went struck out in red), the core
   18 words (or all 100) with IPA, house spelling where the file has one for that form, audio; the live grams on the ladder (free
   word / clitic / affix / fused); the typology line; complexity over time (dashed where the line passes to a daughter); the sound
   changes up to the frame, newest first, with cause and wave source.
4. **Continuum & intelligibility**: equirectangular map (the run's `/api/thumb?proj=equirect` as background) of lects spoken at the
   frame, coloured by language / true family / people; neighbour edges coloured by intelligibility (green > 0.7, amber 0.4-0.7,
   red < 0.4; "hide red"). Side: the pass's `continua` with each link's value, the ends' value, a verdict ("the middle understands
   both neighbours, the two ends do not"), when the ends stopped understanding each other, and a sparkline; plus the same search
   run in the browser at the scrubbed frame. Below: a west-to-east heatmap of every pair in the picked lect's language (falls back
   to its true family when the language has one lect), true family or people.
5. **Names & etymologies**: per people, endonym, glossonym, the land/people/person/language set and exonyms, each with its
   etymology as a vertical chain; its demes' names and place/river names. Until `names` is filled it says so and shows the words
   such names grow from (PERSON, MAN, WOMAN, WE, NAME, EARTH ...) with their chains, and each deme's landscape facts. Any word of
   the picked lect can be traced, with its word family both as a speaker feels it (`roots`) and as a historian reconstructs
   it (`etym_roots`).
6. **Food words & shifts**: routes as hop tables (when, from, to, form before → after, spelling, changes on the way), filter by word
   and people; shifts (when, place, speakers → ruler people, old → new lect, trigger kind + source, substrate words, accent pairs,
   calques), filter by trigger and people.
7. **Checks & voices**: the checks table, the families numbers, and a card per species' voice profile (articulators, cannot make,
   costly, easy, hearing, notes; a "human default" pill when it has no voice of its own).

## Fields read from `languages.json`

Top: `frames_kyr`, `snapshot_concepts`, `etym_nodes`, `lects`, `families`, `intelligibility`, `continua`, `names`, `shifts`,
`food_routes`, `checks`, `profiles`, `landscape`, `format`, `romanization`, `seed`, `romanization_failures`, `timing`; optional
`rules` (see below). Run: `run.json` `meta.lineages[]` (`id`, `name`, `color`), `meta.demes.file`, `meta.languages.file`;
`demes.json` `demes[]` (`id`, `name`, `short`, `lat`, `lon`) and `pairs[]` (`a`, `b`, `first_kyr`, `last_kyr`) for contact.

- lect: `id deme people parent how substrate born_kyr died_kyr end language family_true family_scholars deme_name population
  lexicon{concept: ipa roman pos etym} changes[[kyr, rule, cause, origin_lect, {city}?]] snapshots[[kyr, {c v core typ grams cx}
  | delta]]`
- families: `scholars` (nested `distance`/`children`/`lect`), `languages[] {id name lects}`, `horizon_kyr`, `horizon_by.human`,
  `chance.floor`, `lang_share`, `true_families`, `scholars_families`, `clade_horizon_kyr`, `clades_recovered`, `clades_true`, `shares`
- intelligibility: `pairs [[a, b, [v|null per frame]]]`, `now [[a, b, v]]`; continua: `family chain adjacent ends`
- names (architecture §11 shape): `peoples[p].{endonym, glossonym, set{land people person language}, exonyms[]{by_people by_lect
  ipa roman gloss pattern basis era_kyr relay}}`, `demes[d].{name, places[]{kind ipa roman gloss lect kyr substrate_of}}`; any name
  may carry `etym` (an `etym_nodes` id or an inline list of steps) and it is drawn as a chain
- shifts: `deme kyr from_lect to_lect ruler_lect speakers ruler_people trigger{kind source} substrate_words accent calques`
- food_routes: `concept origin_deme origin_lect kyr ipa roman origin hops[]{deme lect kyr ipa roman from_deme from_lect from_ipa changes}`
- profiles: `source modality articulators make_cost hear register notes`; checks: `name value target pass note`

## What the viewer would like from the data

- **`rules: {rule id: describe}`** (rules.describe in plain words): the change log shows ids (`S151`, `umlaut.i`) and causes only.
- **House spelling in snapshots** (`core_roman` beside `core`): past forms are spelled only where the same IPA occurs in some
  lexicon in the file; the rest show IPA alone.
- **Snapshots for proto lects** are absent (deme `null`); the history starts at the first deme lect's 20 kyr snapshot, which is fine.
- **Feature braces in IPA** (`kʰ{voice=0}`, `cʰ{place=3,voice=0,secondary=2}`): percepts with no IPA letter come out with their
  features; the grid shows `°` with the full form on hover, words show them raw.
- **File size**: E's test file is 125 MB (151 MB earlier); it loads and parses in ~1.3-2 s here, all tabs draw in < 0.2 s, scrubbing
  < 40 ms a frame, so the viewer copes; the 40 MB target is still worth keeping for the owner's disk and the server.
- No server route is needed: everything is static under `/runs/<id>/` plus `/api/speak` (buttons hidden on a 503) and `/api/thumb`.

## Audio (round 5)

Every ▶ calls `/api/speak` (a word) or `/api/speak?sentence=1[&q=1]` (a sentence). The header's **voice** picker chooses
the backend (best available, Piper, eSpeak; ones the server lacks are disabled, from `/api/speak/backends`) and is
remembered per browser (`localStorage` `lang.voice`); beside it a state line says ready / making the sound… / playing… or
why a sound failed. Buttons pulse while loading, light up while playing, stop on a second click. With no backend every ▶
and the picker are hidden. Details: `audio.md`, "Whole sentences and the viewer". Screens of round 5:
`screens/lang-grammar-*.png`, `screens/lang-audio-*.png`.

