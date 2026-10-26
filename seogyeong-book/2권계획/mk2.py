import subprocess
src='vol2-toc-v1'
subprocess.run(['pandoc',src+'.md','-t','latex','-o','body.tex','--wrap=preserve'],check=True)
b=open('body.tex',encoding='utf-8').read()
pre=r'''\documentclass[10pt,a4paper]{article}
\usepackage{fontspec}\setmainfont{Noto Serif CJK KR}\setsansfont{Noto Sans CJK KR}
\usepackage[margin=22mm]{geometry}\usepackage{calc}\newcommand{\real}[1]{#1}\usepackage{longtable,booktabs,array,xurl,hyperref,fancyvrb,framed}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\usepackage{titlesec}\titleformat{\section}{\sffamily\bfseries\Large}{}{0pt}{}\titleformat{\subsection}{\sffamily\bfseries\large}{}{0pt}{}
\setcounter{secnumdepth}{0}
\begin{document}
'''
open('v.tex','w',encoding='utf-8').write(pre+b+'\n\\end{document}\n')
