---
id: PW-1766
title: Windows on ARM and Intel Macs cannot install (piper-tts, numba and onnxruntime wheels)
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: s
impact: low
found_by: lane315
blocked_by: []
relates: [PW-1760]
refs: [uv.lock, pyproject.toml, install.ps1, "install.ps1::Get-Target", "install.sh::platform", planet/language/speak.py, docs/review/plan/installer.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** uv.lock has Python 3.14 wheels for numba, llvmlite and onnxruntime on Apple Silicon (onnxruntime
needs macOS 14 or newer), x86-64 Windows, ARM64 Windows and Linux, but none for Intel Macs. piper-tts (the speech
voices of the languages viewer) has no ARM64 Windows wheel, only a source package that would need a C compiler. The
installers now refuse these machines up front with a plain message, instead of failing halfway through `uv sync`.

If this is never done: an Intel Mac (common until 2020) or a Snapdragon Windows laptop cannot run procgen_world at all,
although only the speech feature needs piper on Windows ARM.

Options: A, make `piper-tts`, `onnx` and `espeakng-loader` an optional extra (`uv sync --extra voice`) that the
installer adds only where wheels exist, so Windows on ARM installs everything but speech. B, for Intel Macs, wait for
numba/llvmlite x86-64 macOS wheels for 3.14, or pin Python 3.13 there if the code allows it. Lean: A now (small), B
only if someone asks.

## Updates
- 2026-11-11: Created from inbox draft draft-windows-arm-and-intel-mac.md (found by lane315).
