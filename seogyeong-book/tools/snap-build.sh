#!/bin/bash
# 사용: tools/snap-build.sh   (빌드 직후 실행) -> buildlog/ 에 tex·log·환경·빌드 기록을 모은다. 이 폴더가 DB(book_typeset_file, book_build)에 들어간다.
cd "$(dirname "$0")/.." || exit 1
mkdir -p buildlog
{ echo "# 빌드 환경 (snap-build.sh)"; date -u +"기록 시각(UTC) %Y-%m-%d %H:%M"; xelatex --version | head -1; pandoc --version | head -1; python3 --version
  echo "## python 패키지"; pip list 2>/dev/null | grep -iE "^(matplotlib|numpy|scipy|networkx|pandas|pypdf|pymupdf|shapely|scikit-learn|scikit-image) "
  echo "## 글꼴"; fc-list | grep -iE "Noto (Sans|Serif) CJK (KR|JP)" | sed 's/:.*style=/ : /' | sort -u | head -20
  echo "## TeX 패키지(템플릿 usepackage)"; grep -ho "\\\\usepackage\[\?[^]]*\]\?{[^}]*}" tools/tpl/book.tex | sort -u
  echo "## 빌드 명령"; echo "export LANG=C.UTF-8 LC_ALL=C.UTF-8; BOOK_VERSION=<라벨> VOLUME=<1|2|3|4> python3 tools/build.py color|bw"; } > buildlog/buildenv.txt
python3 - <<'PY'
import os, re, json, hashlib, gzip, glob, shutil, subprocess
B = "build"; out = []
old = json.load(open("buildlog/builds.json", encoding="utf-8")) if os.path.exists("buildlog/builds.json") else []
ver = os.environ.get("BOOK_VERSION", "")
for pdf in sorted(glob.glob(f"{B}/book-*-vol*.pdf")):
    m = re.search(r"book-(color|bw)-vol(\d)\.pdf", pdf)
    if not m: continue
    mode, vol = m.groups()
    if os.environ.get("VOLUME") and vol != os.environ["VOLUME"]: continue
    b = open(pdf, "rb").read()
    try:
        import pypdf; pages = len(pypdf.PdfReader(pdf).pages)
    except Exception: pages = None
    lg = open(pdf[:-4] + ".log", encoding="utf-8", errors="ignore").read()
    ov = len(re.findall(r"Overfull \\hbox", lg))
    rec = dict(version=ver, volume=vol, mode=mode, pages=pages, pdf_sha256=hashlib.sha256(b).hexdigest(), pdf_bytes=len(b), overfull=ov, note="")
    old = [o for o in old if not (o["volume"] == vol and o["mode"] == mode and o["version"] == ver)] + [rec]
    for ext in ("tex", "log"):
        src = pdf[:-4] + "." + ext
        with open(src, "rb") as f, gzip.open(f"buildlog/{os.path.basename(src)}.gz", "wb") as g: g.write(f.read())
json.dump(old, open("buildlog/builds.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("builds.json", len(old))
PY
