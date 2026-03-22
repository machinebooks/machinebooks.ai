# Extraído de: LibroBugBounty/cap-18-report-bounty.md
# Generar PDF profesional desde Markdown
pandoc report.md \
  --pdf-engine=xelatex \
  --template=security_report.tex \
  -V geometry:margin=2.5cm \
  -V header-includes='\usepackage{fancyhdr}' \
  -o report.pdf
