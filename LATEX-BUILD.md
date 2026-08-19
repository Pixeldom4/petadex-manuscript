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

`latexmk` recorded exactly two rules in [petadex-manuscript.fdb_latexmk](petadex-manuscript.fdb_latexmk):
`pdflatex` and `bibtex petadex-manuscript`. No `-synctex=1` was used (no `.synctex.gz` was
produced), so the build was plain:

```bash
latexmk -pdf petadex-manuscript.tex
```

`latexmk` handles the pdflatex → bibtex → pdflatex → pdflatex loop until `.aux`/`.bbl` converge.

Other equivalent invocations that appear in this repo's history:

```bash
# what .claude/settings.local.json pre-approves (single pass, no bibliography)
pdflatex -interaction=nonstopmode petadex-manuscript.tex

# the manual equivalent of the latexmk loop
pdflatex petadex-manuscript && bibtex petadex-manuscript && pdflatex petadex-manuscript && pdflatex petadex-manuscript
```

To clean: `latexmk -C` (removes the PDF too) or `latexmk -c` (keeps the PDF).

### Document-side setup

- Class: [oup-authoring-template.cls](oup-authoring-template.cls) v1.2 (2025-11-17), the Oxford
  University Press authoring template, **vendored into the repo** — it is not a CTAN package.
  Loaded as `\documentclass[unnumsec,webpdf,modern,large]{oup-authoring-template}`.
- Bibliography style: [oup-abbrvnat.bst](oup-abbrvnat.bst), also vendored. Used via
  `\bibliographystyle{oup-abbrvnat}` + `\bibliography{petadex-references}` (natbib-style,
  BibTeX-only).
- References: [petadex-references.bib](petadex-references.bib) (20 entries as of the last build).
- Figures: PNGs sit in the **repo root**, not in a subfolder. The source declares
  `\graphicspath{{Fig/}}` (inherited from the OUP template), which is a no-op here — the root is
  already on the search path. If you move figures into `Fig/`, that line starts doing real work.
- `NAR.png` is the journal logo pulled into a custom `\ps@opening` page style in the preamble.

### Build artifacts are committed

`.aux`, `.bbl`, `.blg`, `.fls`, `.fdb_latexmk`, `.log`, `.out`, and the `.pdf` are all tracked in
git, and there is no `.gitignore`. That is a choice, not an accident — but it means every rebuild
produces diff noise. See "Optional cleanups" below.

### Verified reproducibility

Copying only `*.tex`, `*.bib`, `*.cls`, `*.bst`, `*.png` into an empty directory and running
`latexmk -pdf petadex-manuscript.tex` exits 0 and produces a PDF byte-identical in size
(2,502,498 bytes, 10 pages) to the committed one. There are no external includes or generated
inputs.

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

BasicTeX ships a minimal set. These are the packages this document actually loads that a plain
BasicTeX install does **not** have:

```bash
sudo tlmgr install \
  algorithmicx algorithms anyfontsize caption changepage crop float footmisc \
  jknapltx listings mdwtools multirow pgf silence sttools subfloat totcount \
  wrapfig xcolor xetexconfig latexmk
```

Package → what needs it:

| Package | Provides | Required by |
|---|---|---|
| `crop`, `xetexconfig` | `crop.sty`, `crop.cfg` | OUP class (crop marks) |
| `caption`, `float`, `subfloat`, `multirow`, `wrapfig` | float/caption/table handling | OUP class |
| `sttools` | `flushend.sty`, `stfloats.sty` | OUP class (two-column balancing) |
| `changepage`, `totcount`, `anyfontsize`, `silence` | layout & log control | OUP class |
| `mdwtools` | `footnote.sty` | OUP class |
| `footmisc` | bottom-aligned footnotes | OUP class |
| `pgf` | `tikz.sty` | OUP class |
| `listings`, `algorithms`, `algorithmicx` | code & pseudocode envs | OUP class |
| `jknapltx` | `mathrsfs.sty` | OUP class |
| `xcolor` | color | OUP class |

Also worth installing, though this build didn't need them:

```bash
sudo tlmgr install cm-super arydshln
```

- **`cm-super`** — without it, pdfTeX has no Type 1 outline for a few text-companion sans glyphs
  and silently falls back to `mktexpk`-generated bitmap fonts (you can see
  `tcss0800.471pk` / `tcss0900.602pk` in [petadex-manuscript.log](petadex-manuscript.log)). Those
  render fuzzy at high zoom and some journals reject bitmap fonts at submission. Installing
  `cm-super` removes the fallback.
- **`arydshln`** — only loaded if you pass the class's `dashline` option.

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

### Optional: pin the recipe so it's not implicit

This repo relies on `latexmk` defaults. If you want the next project to be self-documenting, add
these two files.

**`.latexmkrc`** (project root — `latexmk` picks it up automatically):

```perl
$pdf_mode = 1;             # pdflatex
$bibtex_use = 2;           # run bibtex, and clean .bbl on -C
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
@default_files = ('manuscript.tex');
$clean_ext = 'bbl fdb_latexmk fls synctex.gz';
```

`-synctex=1` enables click-to-source jumping between the PDF viewer and editor — worth having;
this repo's builds ran without it.

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
