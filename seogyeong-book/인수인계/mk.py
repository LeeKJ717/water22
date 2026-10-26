import subprocess,re
t=open('handoff-v12.md',encoding='utf-8').read()
subprocess.run(['pandoc','handoff-v12.md','-t','latex','-o','body.tex','--wrap=preserve'],check=True)
b=open('body.tex',encoding='utf-8').read()
pre=r'''\documentclass[10pt,a4paper]{article}
\usepackage{fontspec}\setmainfont{Noto Serif CJK KR}\setmonofont{Noto Sans Mono CJK KR}
\usepackage[margin=22mm]{geometry}\usepackage{calc}\newcommand{\real}[1]{#1}\usepackage{longtable,booktabs,array,xurl,hyperref,fancyvrb,framed}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newenvironment{Shaded}{}{}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\begin{document}
\begin{center}{\LARGE\bfseries 서경 책 작업 인수인계 v12}\end{center}
'''
open('h.tex','w',encoding='utf-8').write(pre+b+'\n\\end{document}\n')
