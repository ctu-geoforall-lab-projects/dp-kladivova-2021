FILE=linda-kladivova-dp-2021

all:
	pdflatex $(FILE)
	bibtex $(FILE)

clean:
	rm -f *~ *.aux *.log *.out *.bbl *.blg *.loa *.lof \
	*.toc *.lot *.lol

distclean:
	make clean
	rm -f $(FILE).pdf
