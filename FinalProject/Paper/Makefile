## -*- mode: Makefile -*-
##

###############################################################################

DOCUMENTS	:=
DOCUMENTS	+= paper

PDFLATEX	= pdflatex
PDFLATEXFLAGS	= -interaction=nonstopmode -halt-on-error -file-line-error

BIBTEX		= bibtex

TEXFILES	:= $(wildcard *.tex)
BIBTEXFILES	:= $(wildcard *.bib)
FIGFILES	:= $(wildcard figs/*.pdf)

export TEXINPUTS
export BIBINPUTS
TEXINPUTS	= .:./figs::
BIBINPUTS	= .::

###############################################################################

.DELETE_ON_ERROR:

.PHONY: all clean realclean
all::
clean::
realclean::

###

define def-doc-rule
  .PHONY: $1
  all:: $1
  $1: $1.pdf
  $1.pdf: $(TEXFILES) $(BIBTEXFILES) $(FIGFILES)
  $1.pdf: $1.tex
	$$(PDFLATEX) $$(PDFLATEXFLAGS) -draftmode $$<
	- $$(BIBTEX) $$(basename $$<)
	$$(PDFLATEX) $$(PDFLATEXFLAGS) -draftmode $$<
	$$(PDFLATEX) $$(PDFLATEXFLAGS) $$<
  clean::
	$$(RM) $1.aux $1.bbl $1.blg $1.log $1.out $1.synctex.gz
  realclean:: clean
	$$(RM) $1.pdf
endef

$(foreach d,$(DOCUMENTS),$(eval $(call def-doc-rule,$d)))

###############################################################################

## End of file.
