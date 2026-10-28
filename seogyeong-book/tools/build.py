"""build.py - 원고(markdown) → LaTeX → PDF. 사용: python3 build.py [color|bw] [--quick]
원고 안의 매크로: {{키:서식}} 수치, @@fig ...@@, @@tab ...@@, @@refs chNN@@"""
import sys, os, re, csv, json, subprocess, glob, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("color", "bw") else "color"
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)
NUM = json.load(open(os.path.join(ROOT, "그림", "data", "numbers.json"), encoding="utf-8"))

TITLE = "고려 서경(西京)의 위치를 추정하다"
SUBTITLE = "여덟 가지 방법으로 동아시아 고전 지명을 좌표로 옮기기"
AUTHOR = "이광조 지음"
PUBLISHER = "과학과영성출판사"

# (파일, 앞에 넣을 부 제목) - 순서가 곧 목차
CHAPTERS = [
    ("00a-preface", None),
    ("00-intro", None),
    ("p0-intro", None),
    ("01-sources", "사료와 문제 설정"), ("02-prior", None), ("03-critique", None), ("04-db", None),
    ("05-csp", "여덟 가지 기법 가운데 네 가지"), ("06-georef", None), ("07-bayes", None), ("08-lcp", None), ("08z-closing", None),
    ("09a-preface", None), ("09i-intro", None),
    ("09-graph", "여덟 가지 기법 가운데 나머지 네 가지"), ("10-gazetteer", None), ("11-toponym", None), ("12-cross", None), ("12z-closing", None),
    ("13a-preface", None), ("13i-intro", None),
    ("13-compare", "서경 통합 추정"), ("14-conflict", None), ("15-conclusion", None),
    ("16-nwkorea", "지역 확장"), ("17-liao", None), ("18-shandong", None), ("19-manchuria", None), ("19z-closing", None),
    ("p9-closing", None),
    ("A-math", "부록"), ("B-glossary", None), ("C-dbspec", None),
]
REFCH = {"00-intro": "ch00", "01-sources": "ch01", "02-prior": "ch02", "03-critique": "ch03", "04-db": "ch04",
         "05-csp": "ch05", "06-georef": "ch06", "07-bayes": "ch07", "08-lcp": "ch08", "09-graph": "ch09",
         "10-gazetteer": "ch10", "11-toponym": "ch11", "12-cross": "ch12", "13-compare": "ch13", "14-conflict": "ch14",
         "15-conclusion": "ch15", "16-nwkorea": "ch16", "17-liao": "ch17", "18-shandong": "ch18", "19-manchuria": "ch19"}

TEX_ESC = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_"}


def esc(s):
    if s.startswith("$") or "\\" in s:
        return s
    return "".join(TEX_ESC.get(c, c) for c in s)


def num_sub(text, where):
    def f(m):
        key, fmt = m.group(1), m.group(2)
        cur = NUM
        try:
            for part in key.split("."):
                cur = cur[int(part)] if isinstance(cur, list) else cur[part]
        except Exception:
            raise KeyError(f"[{where}] 수치 키 없음: {key}")
        return format(cur, fmt) if fmt else str(cur)
    return re.sub(r"\{\{([A-Za-z0-9_.가-힣]+)(?::([^}]+))?\}\}", f, text)


def md_inline_to_tex(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\textit{\1}", s)
    return s


WIDEMM = 12.0  # 그림 폭 = 본문 130.6mm + 12mm (오른쪽 허용선 168mm 안쪽)
WIDEK = 1.2  # 표 p{}열 폭 배율(130→약 156mm)


def fig_macro(m):
    path, label, cap = [x.strip() for x in m.group(1).split("|", 2)]
    scale = 1.0
    if "@" in label:  # 라벨@0.93 → 그림 폭 배율(오른쪽 허용선을 넘는 그림용)
        label, sc = label.split("@", 1); scale = float(sc)
    cap = esc(cap)
    base = os.path.join(ROOT, "그림", path)
    f = f"{base}-{MODE}.pdf"
    assert os.path.exists(f), f"그림 없음: {f}"
    return ("\n```{=latex}\n\\begin{figure}[!htbp]\\centering\n"
            f"\\makebox[\\linewidth][r]{{\\makebox[\\dimexpr\\linewidth+{WIDEMM}mm\\relax][c]{{\\includegraphics[width={scale}\\dimexpr\\linewidth+{WIDEMM}mm\\relax,height=0.8\\textheight,keepaspectratio]{{{f}}}}}}}\n\\caption{{{cap}}}\\label{{fig:{label}}}\n\\end{{figure}}\n```\n")


def _vw(c):
    """칸 글자의 한 줄 폭(mm): 한글·한자 3.25, 그 밖 1.85, 수식은 글자 수의 1.5배로 어림"""
    c = re.sub(r"\*\*", "", c.strip())
    w = 0.0
    for i, part in enumerate(c.split("$")):
        if i % 2 == 1:
            w += 1.6 * len(re.sub(r"\\[a-zA-Z]+|[{}^_]", "", part)) + 1.0
        else:
            w += sum(3.38 if ord(ch) > 0x2E80 else 1.95 for ch in part)
    return w


def _lines(cell, w):
    """칸 글자를 폭 w(mm)에 줄바꿈했을 때 (줄 수, 마지막 줄이 한두 글자만 남는 고아 여부) — 글자 단위 탐욕 모의."""
    c = re.sub(r"\*\*", "", cell.strip())
    toks = []
    for i, part in enumerate(c.split("$")):
        if i % 2 == 1:
            toks.append(1.6 * len(re.sub(r"\\[a-zA-Z]+|[{}^_]", "", part)) + 1.0)
        else:
            toks += [3.38 if ord(ch) > 0x2E80 else 1.95 for ch in part]
    toks = [t * 1.10 for t in toks]
    n, cur, last = 1, 0.0, 0.0
    for t in toks:
        if cur + t > w and cur > 0:
            n += 1; cur = t
        else:
            cur += t
    orphan = n > 1 and cur < 10.5
    return n, orphan


def alloc_widths(rows, total):
    """열 폭 배분: 짧은 칸만 있는 열은 한 줄 폭을 확보하고, 긴 칸이 있는 열들은 폭 조합을 훑어 줄 수와 한두 글자 고아 줄을 최소로 한다."""
    n = len(rows[0])
    nat = [max(_vw(r[c]) for r in rows) * 1.02 + 0.5 for c in range(n)]
    if sum(nat) <= total:
        extra = (total - sum(nat)) / n
        return [x + extra for x in nat]
    short = [c for c in range(n) if nat[c] <= 32.0]
    longc = [c for c in range(n) if c not in short]
    rem = total - sum(nat[c] for c in short)
    if not longc or rem < 12.0 * len(longc):
        k = total / sum(nat)
        return [x * k for x in nat]
    import itertools
    steps = 24 if len(longc) <= 2 else (16 if len(longc) == 3 else 9)
    best, bw = None, None
    for combo in itertools.product(range(1, steps), repeat=len(longc) - 1):
        if sum(combo) >= steps:
            continue
        parts = list(combo) + [steps - sum(combo)]
        ws = {c: max(12.0, rem * parts[i] / steps) for i, c in enumerate(longc)}
        sc = 0.0
        for r in rows:
            mx = 1
            for c in longc:
                ln, orph = _lines(r[c], ws[c])
                mx = max(mx, ln)
                sc += 0.35 * orph + 0.04 * ln
            sc += mx
        if best is None or sc < best:
            best, bw = sc, ws
    tot = sum(bw.values())
    return [nat[c] if c in short else bw[c] * rem / tot for c in range(n)]



import json
_TALLF = os.path.join(BUILD, "tall.json") if "BUILD" in globals() else None


def _tall():
    try:
        return json.load(open(os.path.join(ROOT, "build", "tall.json"), encoding="utf-8"))
    except Exception:
        return {}


def table_tex(cap_tex, label, hdr_cells, body_rows, spec, note_tex=""):
    """표 한 개를 LaTeX로. 한 쪽에 안 들어가는 표는 build의 점검 결과(tall.json)에 따라 작은 글씨 또는 longtable(머리글 반복)로 낸다."""
    mode = _tall().get(label, "")
    ncol = len(hdr_cells)
    hdr = " & ".join(hdr_cells) + r" \\"
    if mode == "long":
        out = [r"\begingroup\footnotesize\setlength{\LTleft}{-15.4mm}\setlength{\LTright}{\fill}",
               f"\\begin{{longtable}}{{{spec}}}",
               f"\\caption{{{cap_tex}}}\\label{{tab:{label}}}\\\\", r"\toprule", hdr, r"\midrule", r"\endfirsthead",
               f"\\multicolumn{{{ncol}}}{{l}}{{\\footnotesize 표 \\thetable\\ (계속)}}\\\\", r"\toprule", hdr, r"\midrule", r"\endhead",
               r"\bottomrule", r"\endfoot"]
        out += [" & ".join(r) + r" \\" for r in body_rows]
        out += [r"\end{longtable}", r"\endgroup"]
        if note_tex:
            out.append(f"\\par\\vspace{{3pt}}\\parbox{{\\linewidth}}{{\\footnotesize {note_tex}}}")
        return "\n".join(out)
    size = r"\footnotesize" if mode == "small" else r"\small"
    out = [r"\begin{table}[!htbp]\centering" + size, f"\\caption{{{cap_tex}}}\\label{{tab:{label}}}",
           f"\\makebox[\\linewidth][r]{{\\begin{{tabular}}{{{spec}}}\\toprule", hdr, r"\midrule"]
    out += [" & ".join(r) + r" \\" for r in body_rows]
    out += [r"\bottomrule\end{tabular}}"]
    if note_tex:
        out.append(f"\\par\\vspace{{3pt}}\\parbox{{\\linewidth}}{{\\footnotesize {note_tex}}}")
    out.append(r"\end{table}")
    return "\n".join(out)


def tab_macro(m):
    parts = [x.strip() for x in m.group(1).split("|")]
    name, label, cap, spec = parts[:4]
    note = esc(parts[4]) if len(parts) > 4 else ""
    cap = esc(cap)
    f = os.path.join(ROOT, "표", f"{name}.csv")
    assert os.path.exists(f), f"표 없음: {f}"
    rows = list(csv.reader(open(f, encoding="utf-8")))
    ncol = len(rows[0])
    assert all(len(r) == ncol for r in rows), f"표 열 수 불일치: {name}"
    ws = alloc_widths(rows, 146.0 - 4.3 * ncol)
    spec = "".join(f">{{\\raggedright\\arraybackslash}}p{{{w:.1f}mm}}" for w in ws)
    assert all(len(r) == ncol for r in rows), f"표 열 수 불일치: {name}"
    tex = table_tex(cap, label, [esc(c) for c in rows[0]], [[esc(c) for c in r] for r in rows[1:]], spec, note)
    return "\n```{=latex}\n" + tex + "\n```\n"


def _cell(c):
    """표 칸 변환: $..$ 수식은 그대로, 나머지는 이스케이프, **굵게** 처리"""
    c = c.strip()
    parts = c.split("$")
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append("$" + p + "$")
        else:
            p = p.replace("\\", r"\textbackslash{}")
            p = "".join(TEX_ESC.get(ch, ch) for ch in p).replace("~", r"\textasciitilde{}")
            p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
            out.append(p)
    return "".join(out)


_NUMLIKE = re.compile(r"^[\s$+\-−0-9.,%()/~e×\\{}^a-z_=*]*$")


def pipe_tables(text, ch):
    """'Table: 캡션' 줄 뒤의 마크다운 표를 번호 있는 LaTeX 표로 바꾼다(수식 가능, 좌측 여백 쪽으로 확장)."""
    lines = text.split("\n")
    out = []; i = 0; k = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("Table:") and i + 2 < len(lines) and lines[i + 1].strip() == "" and lines[i + 2].startswith("|"):
            cap = ln[len("Table:"):].strip()
            j = i + 2; rows = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c for c in lines[j].strip().strip("|").split("|")]); j += 1
            hdr, body = rows[0], [r for r in rows[2:]]
            n = len(hdr); k += 1
            numeric = [all(_NUMLIKE.match(r[c].strip()) is not None and len(r[c].strip()) < 26 for r in body) for c in range(n)]
            wl = alloc_widths([hdr] + body, 146.0 - 4.3 * n)
            spec = ""
            for c in range(n):
                spec += (f">{{\\centering\\arraybackslash}}p{{{wl[c]:.1f}mm}}" if numeric[c] else f">{{\\raggedright\\arraybackslash}}p{{{wl[c]:.1f}mm}}")
            tex = ["```{=latex}", table_tex(_cell(cap), f"{ch}-w{k}", [_cell(c) for c in hdr], [[_cell(c) for c in r] for r in body], spec), "```"]
            out.extend(tex); i = j
        else:
            out.append(ln); i += 1
    return "\n".join(out)


def refs_macro(m):
    ch = m.group(1).strip()
    f = os.path.join(ROOT, "참고문헌", f"{ch}.txt")
    if not os.path.exists(f):
        return ""
    items = [l.strip() for l in open(f, encoding="utf-8") if l.strip() and not l.startswith("#")]
    items.sort(key=lambda s: s.casefold())
    if not items:
        return ""
    out = ["\n```{=latex}\n\\section*{참고문헌}\\addcontentsline{toc}{section}{참고문헌}\n\\begin{ref-list}"]
    for it in items:
        out.append("\\refitem{" + md_inline_to_tex(esc_ref(it)) + "}")
    out.append("\\end{ref-list}\n```\n")
    return "\n".join(out)


def esc_ref(s):
    out, pos = [], 0
    for m in re.finditer(r"https?://[^\s)]+[^\s).,;]", s):
        out.append("".join(TEX_ESC.get(c, c) for c in s[pos:m.start()]))
        u = "".join(TEX_ESC.get(c, c) for c in m.group(0))
        out.append(re.sub(r"([/\-=&.:_])", r"\1\\allowbreak{}", u).replace("\\%", "\\allowbreak{}\\%"))
        pos = m.end()
    out.append("".join(TEX_ESC.get(c, c) for c in s[pos:]))
    return "".join(out)


def preprocess(name):
    text = open(os.path.join(ROOT, "원고", name + ".md"), encoding="utf-8").read()
    text = num_sub(text, name)
    text = re.sub(r"@@fig\s+(.+?)@@", fig_macro, text, flags=re.S)
    text = re.sub(r"@@tab\s+(.+?)@@", tab_macro, text, flags=re.S)
    text = re.sub(r"@@refs\s+(.+?)@@", refs_macro, text)
    text = pipe_tables(text, name.split("-")[0])
    return text


def pandoc_tex(md_text):
    p = subprocess.run(["pandoc", "-f", "markdown+raw_tex-smart", "-t", "latex", "--top-level-division=chapter", "--wrap=preserve", "--no-highlight"],
                       input=md_text, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    tex = auto_index(p.stdout)
    # 절·소절 제목이 쪽 맨 아래에 홀로 남지 않도록 제목 앞에 필요한 공간을 확보한다
    tex = re.sub(r"(\\hypertarget\{[^}]*\}\{%\n)(\\(?:section|subsection)\{)", lambda m: "\\needspace{4\\baselineskip}\n" + m.group(1) + m.group(2), tex)
    tex = re.sub(r"(\\hypertarget\{[^}]*\}\{%\n)(\\subsubsection\{)", lambda m: "\\needspace{3\\baselineskip}\n" + m.group(1) + m.group(2), tex)
    tex = re.sub(r"\\needspace\{4\\baselineskip\}(\n\\hypertarget\{[^}]*\}\{%\n\\section\{[^\n]*\n\n)\\needspace\{[34]\\baselineskip\}\n", r"\\needspace{8\\baselineskip}\1", tex)
    tex = re.sub(r"\\needspace\{4\\baselineskip\}(\n\\hypertarget\{[^}]*\}\{%\n\\subsection\{[^\n]*\n\n)\\needspace\{3\\baselineskip\}\n", r"\\needspace{7\\baselineskip}\1", tex)
    # 제목 바로 뒤에 표·그림이 오면 그 앞에서 어느 정도 공간을 확보해 제목만 홀로 남지 않게 한다
    tex = re.sub(r"\\needspace\{\d+\\baselineskip\}(\n\\hypertarget\{[^}]*\}\{%\n\\(?:sub)*section\{[^\n]*\n\n(?:```\n)?\\begin\{(?:table|figure|longtable)\})", r"\\needspace{14\\baselineskip}\1", tex)
    return tex


def auto_index(tex):
    """짧은 굵은 글씨(핵심 용어)를 색인에 올린다. 문장형 굵은 글씨(마침표·쉼표로 끝남, 12자 초과)는 제외."""
    def f(m):
        t = m.group(1)
        if len(t) > 14 or re.search(r"[.,;:?!。]$", t) or re.search(r"[!@|\"]", t) or "\\" in t or "{" in t or "$" in t:
            return m.group(0)
        return m.group(0) + "\\index{" + t + "}"
    return re.sub(r"\\textbf\{([^{}]*)\}", f, tex)


VOL = os.environ.get("VOLUME", "")
VOLS = {
    "1": (["p0-intro", "01-sources", "02-prior", "03-critique", "04-db", "p9-closing", "C-dbspec"], "1권 준비편", "p0-preface", ["ch01", "ch02", "ch03", "ch04"]),
    "4": (["13i-intro", "13-compare", "14-conflict", "15-conclusion", "16-nwkorea", "17-liao", "18-shandong", "19-manchuria", "19z-closing"], "4권 통합·적용편", "13a-preface", ["ch13", "ch14", "ch15", "ch16", "ch17", "ch18", "ch19"]),
    "3": (["09i-intro", "09-graph", "10-gazetteer", "11-toponym", "12-cross", "12z-closing"], "3권 실행편", "09a-preface", ["ch09", "ch10", "ch11", "ch12"]),
    "2": (["00-intro", "05-csp", "06-georef", "07-bayes", "08-lcp", "08z-closing", "A-math", "B-glossary"], "2권 방법편", "00a-preface", ["ch00", "ch05", "ch06", "ch07", "ch08"]),
}


def all_refs():
    items = set()
    for f in glob.glob(os.path.join(ROOT, "참고문헌", "ch*.txt")):
        if VOL in VOLS and os.path.basename(f)[:4] not in VOLS[VOL][3]:
            continue
        for l in open(f, encoding="utf-8"):
            l = l.strip()
            if l and not l.startswith("#"):
                items.add(l)
    return sorted(items, key=lambda s: s.casefold())


def front():
    return r"""
\begin{titlepage}\thispagestyle{empty}
\vspace*{28mm}
{\raggedright\sffamily\bfseries\fontsize{21}{32}\selectfont """ + TITLE + r"""\par}
\vspace{10mm}
{\raggedright\sffamily\Large """ + SUBTITLE + r"""\par}
""" + (r"\vspace{12mm}{\raggedright\sffamily\bfseries\Large " + VOLS[VOL][1] + r"\par}" if VOL in VOLS else "") + r"""
\vfill
{\raggedright\large """ + AUTHOR + r"""\par}
\vspace{6mm}
{\raggedright\large """ + PUBLISHER + r"""\par}
\vspace{14mm}
\end{titlepage}
@@PREFACE@@
\clearpage
\chapter*{일러두기}\addcontentsline{toc}{chapter}{일러두기}
""" + "\n" + "@@NOTES@@" + r"""
\clearpage
\tableofcontents
\clearpage
\listoffigures
\clearpage
\listoftables
\clearpage
"""


OPEN = {
    "00-intro": ("ch00/fig0-map", "이 책의 지도"),
    "p0-intro": ("ch00/fig0-map", "이 책의 지도"),
    "p9-closing": ("ch00/fig0-map", "이 책의 지도와 다음 권으로 가는 길"),
    "01-sources": ("ch01/fig1-sources", "사료의 여섯 무리와 뽑아내는 증거의 유형"),
    "02-prior": ("ch02/fig02-1-regions", "이 책의 연구 지역과 지역 가설의 틀"),
    "03-critique": ("ch03/fig3-unit-direction", "단위는 구간으로, 방향은 부채꼴로 다룬다"),
    "04-db": ("ch04/fig4-db", "증거 DB의 표 구성(개략도)"),
    "05-csp": ("ch05/fig05-2-layers", "제약을 하나씩 더하면 가능한 영역이 줄어든다(가상 세계)"),
    "06-georef": ("ch06/fig06-2-warp", "옛 지도의 격자를 현대 좌표로 옮긴 모양(가상 세계)"),
    "07-bayes": ("ch07/fig07-1-bayes", "사전분포, 우도, 사후분포(가상 세계)"),
    "08-lcp": ("ch08/fig08-1-isochrone", "등시간선과 최소비용 경로(가상 세계)"),
    "08z-closing": ("ch00/fig0-map", "이 책의 지도와 다음 권으로 가는 길"),
    "13i-intro": ("ch00/fig0-map", "이 책의 지도"),
    "13-compare": ("ch13/fig13-b-flow", "비교의 흐름(가상 세계)"),
    "14-conflict": ("ch14/fig14-b-flow", "충돌 진단의 흐름"),
    "15-conclusion": ("ch15/fig15-b-blanks", "결론 문장의 빈칸"),
    "16-nwkorea": ("ch16/fig16-b-scale", "한반도 서북부의 눈금"),
    "17-liao": ("ch17/fig17-b-crossing", "요하 유역의 건넘 지점"),
    "18-shandong": ("ch18/fig18-b-course", "산동 지역의 항로"),
    "19-manchuria": ("ch19/fig19-c-xijing", "만주의 서경 후보"),
    "19z-closing": ("ch00/fig0-map", "이 책의 지도"),
    "09i-intro": ("ch00/fig0-map", "이 책의 지도"),
    "09-graph": ("ch09/fig09-2-graph", "지명 사이의 연결을 그물로 나타낸 모양(가상 세계)"),
    "10-gazetteer": ("ch10/fig10-1-gazetteer", "지명 사전의 구성(가상 세계)"),
    "11-toponym": ("ch11/fig11-1-morph", "지명 글자의 구성(개략도)"),
    "12-cross": ("ch12/fig12-1-eight", "일곱 기법과 합친 결과의 사후분포(가상 세계)"),
    "12z-closing": ("ch00/fig0-map", "이 책의 지도와 다음 권으로 가는 길"),
    "A-math": None, "B-glossary": None,
    "C-dbspec": ("ch04/fig4-db", "증거 DB의 표 구성(개략도)"),
}


def add_opener(name, tex):
    """장 첫 쪽(오른쪽): 장 제목 + 대표 그림 + 이 장의 차례, 다음 쪽(뒷면)부터 소개가 시작된다."""
    if name not in OPEN:
        return tex
    # 번호 없는 절도 장 차례에 올린다
    tex = re.sub(r"(\\section\*\{([^{}]*)\}\\label\{[^{}]*\}\})(?!\s*\\addcontentsline)", lambda m: m.group(1) + "\\addcontentsline{toc}{section}{" + m.group(2) + "}", tex)
    lines = tex.split("\n")
    k = next(i for i, l in enumerate(lines) if l.startswith("\\chapter"))
    j = k + 1 if k + 1 < len(lines) and lines[k + 1].startswith("\\addcontentsline") else k
    blk = ["\\par\\vspace{3mm}"]
    if OPEN[name]:
        fig, cap = OPEN[name]
        f = os.path.join(ROOT, "그림", f"{fig}-{MODE}.pdf")
        assert os.path.exists(f), f"그림 없음: {f}"
        blk.append("\\begin{center}\\includegraphics[width=\\linewidth,height=" + ("0.22" if name in ("05-csp", "06-georef", "07-bayes", "08-lcp") else "0.40") + "\\textheight,keepaspectratio]{" + f + "}\\\\[3pt]{\\footnotesize 대표 그림: " + esc(cap) + "}\\end{center}\\vspace{3mm}")
    blk.append("\\noindent{\\sffamily\\bfseries 이 장의 차례}\\par\\vspace{2pt}\\hrule\\vspace{4pt}\n\\etocmulticolstyle[2]{}")
    blk.append("{\\" + ("scriptsize" if name in ("05-csp", "06-georef", "07-bayes", "08-lcp") else "footnotesize") + "\\localtableofcontents}\\clearpage")
    lines[j + 1:j + 1] = blk
    return "\\cleardoublepage\n" + "\n".join(lines)


def build():
    body = []
    for name, part in CHAPTERS:
        if name in ("00a-preface", "p0-preface", "09a-preface", "13a-preface"):
            continue
        if VOL in VOLS and name not in VOLS[VOL][0]:
            continue
        if part:
            body.append("\\part{" + part + "}\n")
        if VOL == "4" and name == "13-compare":
            body.append("\\setcounter{chapter}{12}\n")
        if VOL == "3" and name == "09-graph":
            body.append("\\setcounter{chapter}{8}\n")
        if VOL == "2" and name == "05-csp":
            body.append("\\setcounter{chapter}{4}\n")
        body.append(add_opener(name, pandoc_tex(preprocess(name))))
    notes = pandoc_tex(num_sub(open(os.path.join(ROOT, "원고", "notes.md"), encoding="utf-8").read(), "notes"))
    fr = front().replace("@@NOTES@@", notes).replace("@@PREFACE@@", pandoc_tex(preprocess(VOLS[VOL][2] if VOL in VOLS else "00a-preface")))
    # 부록 D(선행연구 목록, 자동)
    d = ["\\clearpage\\chapter*{부록 D 선행연구 목록}\\addcontentsline{toc}{chapter}{부록 D 선행연구 목록 (APA 7판)}\n\\begin{ref-list}"]
    for it in all_refs():
        d.append("\\refitem{" + md_inline_to_tex(esc_ref(it)) + "}")
    d.append("\\end{ref-list}\n")
    back = "\n".join(d) + "\n\\clearpage\\printindex\n\\addcontentsline{toc}{chapter}{색인}\n" + "\\clearpage\n" + open(os.path.join(ROOT, "표지", "colophon-body.tex"), encoding="utf-8").read() + "\n\\clearpage\\null\\thispagestyle{empty}\n"
    tpl = open(os.path.join(ROOT, "tools", "tpl", "book.tex"), encoding="utf-8").read()
    tex = tpl.replace("@@FRONT@@", fr).replace("@@BODY@@", "\n".join(body)).replace("@@BACK@@", back)
    out = os.path.join(BUILD, f"book-{MODE}" + (f"-vol{VOL}" if VOL in VOLS else "") + ".tex")
    open(out, "w", encoding="utf-8").write(tex)
    return out


def run_tex(tex):
    d = os.path.dirname(tex)
    base = os.path.basename(tex)
    stem = base[:-4]
    quick = "--quick" in sys.argv
    n = 1 if quick else 3
    for i in range(n):
        p = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", base], cwd=d, capture_output=True, text=True)
        if p.returncode:
            print(p.stdout[-3000:])
            raise SystemExit("xelatex 실패")
        if i == 0 and not quick:
            subprocess.run(["makeindex", "-q", stem + ".idx"], cwd=d, capture_output=True)
    log = open(os.path.join(d, stem + ".log"), encoding="utf-8", errors="ignore").read()
    ov = len(re.findall(r"Overfull \\hbox", log))
    undef = re.findall(r"LaTeX Warning: (?:Reference|Citation) `([^']+)' .*undefined", log)
    print(f"{stem}.pdf 완료 | Overfull hbox {ov}건 | 정의되지 않은 참조 {len(set(undef))}건 {sorted(set(undef))[:10]}")


def check_tall(tex):
    """로그의 'Float too large' 경고를 표 라벨로 옮겨 tall.json에 적는다. 새로 찾았으면 True."""
    d = os.path.dirname(tex)
    log = open(os.path.join(d, os.path.basename(tex)[:-4] + ".log"), encoding="utf-8", errors="ignore").read()
    lines = open(tex, encoding="utf-8").read().split("\n")
    cur = _tall(); new = False
    for m in re.finditer(r"Float too large for page by ([\d.]+)pt on input line (\d+)", log):
        over, ln = float(m.group(1)), int(m.group(2))
        lab = None
        for k in range(ln - 1, max(0, ln - 400), -1):
            mm = re.search(r"\\label\{tab:([^}]*)\}", lines[k])
            if mm: lab = mm.group(1); break
        if lab:
            mode = "small" if over < 40 and cur.get(lab) != "small" and cur.get(lab) != "long" else "long"
            if cur.get(lab) != mode:
                cur[lab] = mode; new = True
                print(f"  표 {lab}: 쪽보다 {over:.0f}pt 큼 -> {mode}")
    if new:
        os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
        json.dump(cur, open(os.path.join(ROOT, "build", "tall.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return new


if __name__ == "__main__":
    t = build()
    run_tex(t)
    for _ in range(3):
        if not check_tall(t):
            break
        t = build()
        run_tex(t)
