LATEX       = pdflatex
BASH        = bash -c
ECHO        = echo
RM          = rm -rf

TMP_SUFFS   = aux bbl blg log dvi ps eps out
RM_TMP      = ${RM} $(foreach suff, ${TMP_SUFFS}, *.${suff})

CHECK_RERUN = grep Rerun $*.log

ALL_FILES = cv.pdf pubs.pdf cv_pubs.pdf biosketch.pdf

all: ${ALL_FILES}

%.pdf: %.tex cvstyle.tex pubs_ref.tex pubs_unref.tex pubs.json other_pubs.json
	${LATEX} $<
	${LATEX} $<

cv_pubs.pdf: cv.tex pubs_*.tex cvstyle.tex pubs.json other_pubs.json
	${LATEX} -jobname=cv_pubs "\def\withpubs{}\input{cv}"
	${LATEX} -jobname=cv_pubs "\def\withpubs{}\input{cv}"

clean:
	${RM_TMP} ${ALL_FILES}
