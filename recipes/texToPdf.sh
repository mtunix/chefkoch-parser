for i in *.tex; do
	pdflatex --interaction=batchmode $i >> /dev/null 2>&1
done
