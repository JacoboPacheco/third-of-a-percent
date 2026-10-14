# Claims audit reports

Point-in-time reports from independent audit passes over the claims in the README and on the page. Each report describes the text as it stood when the report was written; the findings were fixed in later commits. A verdict count at the top of a report (for example the 11 CONTRADICTED, 24 OVERSTATED and 6 STALE of `CLAIMS.md`) therefore describes that earlier text, not the current page.

| Report | What it audited |
|---|---|
| `CLAIMS.md` | the first audit: README, page and linked READMEs |
| `CLAIMS-2.md` | claims new or changed since the first audit |
| `CLAIMS-3.md`, `CLAIMS-3-input.md`, `CLAIMS-3-recheck.md` | the real-program timing text |
| `CLAIMS-4.md`, `CLAIMS-4-input.md` | the layout sweep, the PGO column and the live test of `tools/lostloops` |
| `CLAIMS-5.md` | the text of the click-first redesign |
| `CLAIMS-6.md` | the newer-toolchain and environment sections |
| `CLAIMS-7.md` | the contrast band, the mechanism demo, the hero captions and the section gists; the most recent report |

Later reports supersede earlier ones for the text they cover.

Commit hashes cited in these reports refer to the original development history, which is not published here; they do not resolve in this repository. Most reports carry their date.

The audit scripts (`recompute*.py`, `render*.py`, `links*.py`, `audit6_recompute*.py`) and their raw output files (`page-text*.txt`, `recompute*-out.txt`, `links*.txt`, `runs-2.txt`, `audit6_out.txt`) were working files and are not published. The tags in square brackets in the tables ([P2], [C1], [I1] and so on) refer to lines of those output files, so the tables cannot be re-run from this repository. Rows that audited unpublished project notes are left out; the counts at the top of `CLAIMS.md` and `CLAIMS-2.md` include them. The figures themselves can be recomputed from `results/`; `python scripts/check.py` does this without a compiler.
