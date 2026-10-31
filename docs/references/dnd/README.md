# D&D 5e rulebooks (local reference only)

`phb-5e.pdf` and `dmg-5e.pdf` are the owner's own copyrighted books, copied here for local
reference. `docs/references/**/*.pdf` and `docs/references/dnd/.cache/` are gitignored.

**Never commit the PDFs, and never commit any text extracted from them** (no excerpts dumped
into docs, tickets or fixtures beyond a short quoted fact with its citation).

## Searching them (agents)

```
uv run python tools/rulebook.py index                      # once; fills .cache/ (about 30 s)
uv run python tools/rulebook.py search "gold\s*dragon" --book dmg --pages 302-305 --context 1
uv run python tools/rulebook.py page dmg 303 --split       # --split reads two-column pages left, then right
uv run python tools/rulebook.py page phb 112               # --pdf treats the number as a PDF page
```

Hits print as `DMG p.303 (pdf page 303): <line>`. **Cite book + printed page** (for example
"DMG p. 303, Appendix B, Forest monsters"), never the PDF page.

- The text layer is OCR: expect noise ("Flu mph", "Aying" for "flying", spaced-out headings).
  Use loose regexes (`dra\s*gon`) and read the page before relying on a line.
- `-layout` extraction is used; it keeps table rows together. On two-column pages a hit line
  can contain text from both columns, so read the page with `--split`.

## Page offsets

- **DMG:** printed page = PDF page, for every page (checked against about 90 printed footers).
  Appendix B "Monsters by environment" is p. 302-305 (lists for the arctic through urban
  environments) with the by-challenge-rating lists following on p. 306-309.
- **PHB:** the scan has no page numbers in its text and about 27 pages are missing, so the
  offset (printed - PDF) creeps from 1 (intro) to 3 (chapter 1, p. 11), 6 (classes, p. 46-119),
  16 (combat, p. 189), 19 to 23 (spell descriptions, p. 211-289). The stretches that were
  anchored (TOC, index, known spell pages) are stored in `PHB_RUNS` in the tool. A PDF page
  between two anchored stretches prints as a range, e.g. `PHB p.232-233?`: check the page
  before citing it exactly. Pages after pdf 270 (appendices B-E, index) print as a range such as `PHB p.294-296?`.
