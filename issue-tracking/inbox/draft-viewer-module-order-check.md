---
title: "Viewer tests: catch a module that touches another before it has loaded (the blank-page error a circular import can cause)"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: viewer-lane-51
blocked_by: []
relates: []
refs: [tests/test_viewer_globe.py, viewer/globe/main.js]
---

## Description
In plain words. The globe viewer's modules import each other in a circle. That is allowed, but the code each module runs as it loads must not use another module's values before that module has loaded. If it does, the page stays blank with "Cannot access 'x' before initialization". During the split this happened three times, and I caught it with a throwaway script. The tests we keep would not catch a new case. They check that every module parses and that the imports link, but not the order modules run in.

What exists:
- tests/test_viewer_globe.py checks parsing, linking, and that main.js reaches every module.
- The lane-51 scratch script (evalorder.mjs, not committed) did the order check: it parsed every module with acorn and eslint-scope, worked out the browser's evaluation order (depth-first from main.js), and flagged top-level code that reads, or calls into, a binding from a module later in that order.
- It had two false positives: closures that only read `OCEAN` when called.

Options:
- A. **Run it in a browser.** A Playwright smoke test that opens index.html on a tiny fixture world and fails on any page error. It catches this and much more, but needs Chrome and a fixture.
- B. **Commit the static checker** as a test. It needs acorn and eslint-scope from npm, which the repo doesn't use yet.
- C. **Evaluate the modules for real** in node vm, with stand-ins for three and the DOM. This is close to what test_layers_table_consistent does for layers.js alone. The stand-ins for the DOM are the fiddly part.

Lean A. It is also the logic test the audit asked for, and clicking every layer button would have caught the peoples-run Plates / Crust age error that lane 51 fixed.
