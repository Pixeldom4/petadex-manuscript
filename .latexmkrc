$pdf_mode = 1;             # pdflatex
$bibtex_use = 2;           # run bibtex, and clean .bbl on -C
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
@default_files = ('petadex-manuscript.tex');
$clean_ext = 'bbl fdb_latexmk fls synctex.gz';
