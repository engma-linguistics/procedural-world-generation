---
title: Viewer play button for words (call /api/speak)
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: lang-design
blocked_by: []
relates: [PW-1423, PW-986]
refs: [planet/language/speak.py::speak, planet/server.py::speak, planet/language/data/ipa_to_speech.tsv, docs/review/language/audio.md, docs/review/language/audio/, tests/test_language_speak.py]
---

## Description
In plain words: words of the generated languages can now be heard, but only from the command line (`planet speak`) or
by typing the URL. Daniel uses the viewer, not the CLI, so until the viewer has a play button he can't hear them.

The server has `GET /api/speak?ipa=<url-encoded IPA>&people=<lineage id>` returning `audio/wav` (cached in memory; 400
for IPA it cannot map, 503 when no speech backend is installed). The viewer should put a small play button next to every
IPA word it shows (lexicon, names, the brief), and play it with
`new Audio('/api/speak?ipa=' + encodeURIComponent(ipa) + '&people=' + encodeURIComponent(id)).play()`.
On 503, hide the button. `people` should be the lineage id from the dnd sample tree (voice profiles are keyed by it).

Piper's voice (the natural-sounding default) is a data download under `data/language/tts/piper/` (steps in
docs/review/language/audio.md); without it the server falls back to the robotic eSpeak voice.
- [ ] play button on IPA words in the language panel
- [ ] button hidden when the route answers 503
