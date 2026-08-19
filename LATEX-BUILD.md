# LaTeX build setup

How this manuscript is compiled, and how to reproduce the same toolchain in a new project.

## What is actually configured

There is **no build config checked into this repo** — no `Makefile`, no `latexmkrc`, no
`.vscode/settings.json`, no CI. The build is entirely "stock `latexmk` against a local TeX Live
install." Everything below was reconstructed from the build artifacts
(`petadex-manuscript.log`, `.fdb_latexmk`, `.fls`, `.blg`) plus the machine's TeX installation.

### Toolchain

| Component | Value |
|---|---|
| Distribution | TeX Live **2026 basic** (BasicTeX), at `/usr/local/texlive/2026basic` |
| Binaries on `PATH` | `/Library/TeX/texbin` (symlinks) |
| Engine | **pdfTeX** 3.141592653-2.6-1.40.29 (`pdflatex`) — *not* XeLaTeX or LuaLaTeX |
| Bibliography | **BibTeX** 0.99e — *not* biber/biblatex |
| Driver | **latexmk** 4.88 |
| Format | LaTeX2e 2025-11-01, L3 2026-03-20 |
| Editor extension | VS Code `james-yu.latex-workshop` 10.14.0 (installed, but with **no** user or workspace settings — it runs on its built-in defaults) |

### The build recipe

A [.latexmkrc](.latexmkrc) is now checked in (it wasn't originally — see git history if you want
the archaeology of why). It pins `$pdf_mode = 1`, `$bibtex_use = 2`, and `-synctex=1`, so the
recipe is just:

```bash
latexmk -pdf petadex-manuscript.tex     # reads .latexmkrc automatically
```

`latexmk` handles the pdflatex → bibtex → pdflatex → pdflatex loop until `.aux`/`.bbl` converge.
`.claude/settings.local.json` pre-approves exactly this command (plus `latexmk -c` for cleanup) —
it used to pre-approve a bare single-pass `pdflatex ...` with no bibtex step, which silently left
the bibliography stale on any `.bib` edit; that's been fixed, don't revert it back to a raw
`pdflatex` call.

To clean: `latexmk -C` (removes the PDF too) or `latexmk -c` (keeps the PDF, per `$clean_ext` in
`.latexmkrc`).

### Document-side setup

As of 2026-08-19 this repo targets **Nature Communications** (Nature Portfolio house style),
not the original NAR/OUP submission. The v1 NAR-formatted manuscript, its figures, its populated
bibliography, and the OUP template files it depended on are preserved in
[archive/v1-petadex-manuscript/](archive/v1-petadex-manuscript/) — that folder is a complete,
independently buildable snapshot of the original submission (copy it out and `latexmk -pdf` it if
you ever need to rebuild the NAR version).

- Class: [sn-jnl.cls](sn-jnl.cls), the official Springer Nature LaTeX authoring template
  (v3.1, December 2024), **vendored into the repo** — like the OUP template before it, this is
  not a CTAN package; it ships from Springer Nature's own LaTeX Author Support page. Loaded as
  `\documentclass[pdflatex,sn-nature]{sn-jnl}`. The `sn-nature` option is the reference style
  Nature Portfolio journals use exclusively; the same `sn-jnl.cls` also serves every other
  Springer/BMC journal via a different option (`sn-basic`, `sn-vancouver-num`, etc. — see the
  vendored `user-manual.pdf` in the original template zip if you ever need a different style).
- Bibliography style: [sn-nature.bst](sn-nature.bst), also vendored (one of eight `.bst` files
  Springer Nature ships; only the one this document uses was pulled in). The class auto-sets
  `\bibliographystyle{sn-nature}` from the `sn-nature` documentclass option — do **not** add an
  explicit `\bibliographystyle{...}` call, it's redundant and can conflict. Used with
  `\bibliography{petadex-references}` (natbib-based, BibTeX-only, same as before).
- References: [petadex-references.bib](petadex-references.bib) is **empty** — the populated v1
  bibliography was archived (see above). Start adding entries for the new manuscript here.
- Figures: none currently referenced — the v1 PNGs were archived along with the v1 manuscript.
  Drop new figures in the repo root (no `\graphicspath` is declared in the new scaffold).
- Section numbering: the scaffold sets `\unnumbered` in the preamble, matching Nature Portfolio's
  house style of unnumbered section heads (`Introduction`, not `1 Introduction`). Remove it if a
  numbered layout is ever needed.
- `NAR.png` (the old NAR journal-logo header hack) is gone — `sn-jnl.cls` handles its own running
  heads/footers, no custom `\ps@opening` override is needed or present.

### Build artifacts are no longer committed

A [.gitignore](.gitignore) now excludes `.aux/.bbl/.blg/.fdb_latexmk/.fls/.log/.out/.synctex.gz/.toc`.
These files used to be tracked (with no `.gitignore` at all), which produced diff noise on every
rebuild and — worse — baked this machine's local absolute paths
(`/Users/Pixel/Library/texlive/...`) into git history via `.fls`/`.log`/`.fdb_latexmk`. The `.pdf`
itself is still meant to be tracked once the manuscript has real content; the current
`petadex-manuscript.pdf` is a placeholder render of the empty scaffold and hasn't been added to
git yet — that's a deliberate pause, not an oversight, so a near-blank PDF doesn't sit in history
next to the real one.

### Verified reproducibility

The `sn-jnl.cls`/`sn-nature.bst` scaffold was test-built with `latexmk -pdf -gg` (forced full
rebuild) on 2026-08-19: exits 0, no `!`-errors, no missing-package errors, produces a 2-page PDF
(title/author block + empty section skeleton — expected, since the scaffold currently has no
body content). The only warnings are a `hyperref` bookmark-depth notice from the `\unnumbered`
option and natbib's expected "empty `thebibliography`" notice (the `.bib` is intentionally
empty). Re-verify page count/size once real content and citations are added — the old
"byte-identical to N bytes" claim from the NAR/OUP version no longer applies to this scaffold;
see [archive/v1-petadex-manuscript/](archive/v1-petadex-manuscript/) if you need that original
reproducibility check.

---

## Replicating this on a new project

### 1. Install the distribution

**macOS (what this machine uses — BasicTeX, ~100 MB):**

```bash
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"   # or open a new shell; puts /Library/TeX/texbin on PATH
sudo tlmgr update --self
```

**macOS (simplest, ~5 GB — skip step 2 entirely):**

```bash
brew install --cask mactex        # full TeX Live, everything below is already present
```

**Linux:** `sudo apt install texlive-full latexmk`, or install upstream TeX Live and pick
`scheme-full`.

### 2. Install the packages BasicTeX is missing

BasicTeX ships a minimal set. These are the packages the **current** (`sn-jnl.cls`, Nature
Communications) scaffold actually loads that a plain BasicTeX install does **not** have:

```bash
sudo tlmgr install jknapltx wrapfig xcolor latexmk
```

Package → what needs it:

| Package | Provides | Required by |
|---|---|---|
| `jknapltx` | `mathrsfs.sty` | `sn-jnl.cls` |
| `wrapfig` | `wrapfig.sty` | `sn-jnl.cls` |
| `xcolor` | color | manually loaded in [petadex-manuscript.tex](petadex-manuscript.tex) |

`sn-jnl.cls` also loads `geometry`, `hyperref`, `natbib`, `amsthm`, `rotating`, and `appendix`,
but those were already present on this machine's BasicTeX install (likely pulled in earlier by
the now-archived OUP template's own requirements) — the build never hit a missing-package error
for them. If you're setting this up on a genuinely bare BasicTeX install and one of those turns
up missing, install it the same way (see the fallback note below).

The previous (NAR/OUP) package list — `algorithmicx`, `algorithms`, `anyfontsize`, `caption`,
`changepage`, `crop`, `float`, `footmisc`, `listings`, `mdwtools`, `multirow`, `pgf`, `silence`,
`sttools`, `subfloat`, `totcount`, `xetexconfig` — was specific to
[archive/v1-petadex-manuscript/oup-authoring-template.cls](archive/v1-petadex-manuscript/oup-authoring-template.cls)
and is not needed for the current scaffold; it's kept here for the record in case that archived
version is ever rebuilt.

Also worth installing, though this build didn't need them:

```bash
sudo tlmgr install cm-super arydshln
```

- **`cm-super`** — without it, pdfTeX has no Type 1 outline for a few text-companion glyphs and
  silently falls back to `mktexpk`-generated bitmap fonts (you can see e.g. `tcrm1000.602pk` in
  [petadex-manuscript.log](petadex-manuscript.log) — still present with `sn-jnl.cls`, same root
  cause as before). Those render fuzzy at high zoom and some journals reject bitmap fonts at
  submission. Installing `cm-super` removes the fallback.
- **`arydshln`** — not currently loaded by `sn-jnl.cls`'s `sn-nature` option; only relevant if a
  future package or table needs dashed array/tabular lines.

If a build fails on a missing `foo.sty`, find its package with `tlmgr search --global --file foo.sty`
and `sudo tlmgr install <pkg>`.

### 3. Lay out the new project

```
myproject/
├── manuscript.tex
├── references.bib
├── <journal-template>.cls      # vendored, like this repo does
├── <journal-style>.bst         # vendored
└── *.png / Fig/                # figures
```

Vendoring the `.cls`/`.bst` is the right call for journal templates — publishers ship them as
downloads, they are not on CTAN, and versions drift. Keep them in git.

### 4. Build

```bash
latexmk -pdf manuscript.tex     # full loop, incremental
latexmk -pdf -pvc manuscript.tex # watch mode: rebuild on save
latexmk -c                       # clean aux files, keep PDF
```

### Pin the recipe so it's not implicit

This repo does this already — [.latexmkrc](.latexmkrc) and [.gitignore](.gitignore) are both
checked in at the root. For a new project, copy the same pattern:

**`.latexmkrc`** (project root — `latexmk` picks it up automatically):

```perl
$pdf_mode = 1;             # pdflatex
$bibtex_use = 2;           # run bibtex, and clean .bbl on -C
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
@default_files = ('manuscript.tex');
$clean_ext = 'bbl fdb_latexmk fls synctex.gz';
```

`-synctex=1` enables click-to-source jumping between the PDF viewer and editor.

**`.gitignore`:**

```gitignore
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
```

Keep `*.pdf` tracked if you want the rendered manuscript in the repo (as here); otherwise add it.

### Optional: VS Code

With `james-yu.latex-workshop` installed, <kbd>Cmd</kbd>+<kbd>Alt</kbd>+<kbd>B</kbd> builds and
<kbd>Cmd</kbd>+<kbd>Alt</kbd>+<kbd>V</kbd> opens the PDF viewer. Its default recipe is already
`latexmk`, so no configuration is needed. To make it explicit in `.vscode/settings.json`:

```json
{
  "latex-workshop.latex.recipe.default": "latexmk",
  "latex-workshop.latex.autoBuild.run": "onFileChange",
  "latex-workshop.view.pdf.viewer": "tab"
}
```

If a `.latexmkrc` is present, LaTeX Workshop's `latexmk` recipe honours it.
