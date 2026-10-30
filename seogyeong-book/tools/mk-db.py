"""mk-db.py - 책 원고·표·그림·참고문헌·실험 결과를 파싱해 placeloc.sqlite에 저장한다.
사용: python3 tools/mk-db.py [출력경로]   (기본 build/placeloc.sqlite). 매번 새로 만든다."""
import sys, os, re, csv, json, glob, hashlib, sqlite3, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "placeloc.sqlite")
VERSION = os.environ.get("BOOK_VERSION", "v5")
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("bld", os.path.join(os.path.dirname(__file__), "build.py"))
src = open(os.path.join(os.path.dirname(__file__), "build.py"), encoding="utf-8").read()
CH = re.search(r"CHAPTERS = \[(.*?)\n\]", src, re.S).group(1)
CHAPTERS = [(a, b) for a, b in re.findall(r'\("([^"]+)",\s*(None|"[^"]*")\)', CH)]
CHAPTERS = [(a, None if b == "None" else b.strip('"')) for a, b in CHAPTERS]
REFCH = dict(re.findall(r'"([0-9A-Za-z\-]+)":\s*"(ch\d\d)"', src))
TECH = {f"ch{n:02d}": n - 4 for n in range(5, 13)}  # ch05=1 … ch12=8
REGION = {"ch16": "H0 한반도 서북부", "ch17": "H1 요하", "ch18": "H2 산동", "ch19": "H3 만주"}

def sha(b): return hashlib.sha256(b).hexdigest()
def rd(p): return open(p, encoding="utf-8").read()

if os.path.exists(OUT): os.remove(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
db = sqlite3.connect(OUT)
db.executescript(rd(os.path.join(ROOT, "tools/collect/placeloc-schema-v1.sql")))
db.executescript(rd(os.path.join(ROOT, "tools/collect/book-schema-v1.sql")))
now = datetime.date.today().isoformat()
db.executemany("INSERT INTO book_meta VALUES (?,?)", [
    ("title", "고려 서경(西京)의 위치를 추정하다"), ("subtitle", "여덟 가지 기법으로 동아시아 고전 지명을 좌표로 옮기기"),
    ("author", "이광조"), ("publisher", "과학과영성출판사"), ("version", VERSION), ("built", now),
    ("edit_rule", "수정 권위는 book_section.body_md. 고친 뒤 tools/db-edit.py export → build.py"),
])

# ---- 장·절·블록
HEAD = re.compile(r"^(#{1,3}) +(.*)$")
def split_sections(text):
    secs, cur, fence = [], None, False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```") or line.strip() == "$$" and False: fence = not fence
        m = None if fence else HEAD.match(line.rstrip("\n"))
        if m:
            if cur: secs.append(cur)
            cur = [len(m.group(1)), m.group(2), line]
        else:
            if cur is None: cur = [0, "", ""]
            cur[2] += line
    if cur: secs.append(cur)
    return secs

def blocks(body):
    out, para, math = [], [], False
    def flush():
        nonlocal para
        t = "".join(para).rstrip("\n")
        if t.strip():
            if t.startswith("@@fig"): k = "fig"
            elif t.startswith("@@tab"): k = "tab"
            elif t.startswith("@@refs"): k = "refs"
            elif t.startswith("$$"): k = "math"
            elif t.startswith(">"): k = "quote"
            elif re.match(r"\s*([-*]|\d+\.)\s", t): k = "list"
            elif t.startswith("#"): k = "heading"
            elif t.startswith("```"): k = "code"
            else: k = "para"
            out.append((k, t))
        para = []
    for line in body.splitlines(keepends=True):
        if line.strip().startswith("$$"):
            if not math and line.strip() != "$$" and line.strip().endswith("$$") and len(line.strip()) > 2:
                para.append(line); continue
            math = not math if line.strip() == "$$" else math
        if not math and not line.strip(): flush()
        else: para.append(line)
    flush()
    return out

for i, (f, part) in enumerate(CHAPTERS):
    p = os.path.join(ROOT, "원고", f + ".md")
    t = rd(p)
    title = re.match(r"#\s+(.*)", t).group(1) if t.startswith("#") else f
    cur = db.execute("INSERT INTO book_chapter(file,ord,part_title,title,ref_key,n_chars,md_sha256) VALUES(?,?,?,?,?,?,?)",
                     (f, i, part, title, REFCH.get(f), len(t), sha(t.encode()))).lastrowid
    for j, (lv, h, body) in enumerate(split_sections(t)):
        sid = db.execute("INSERT INTO book_section(ch_id,ord,level,heading,body_md,n_chars) VALUES(?,?,?,?,?,?)",
                         (cur, j, lv, h, body, len(body))).lastrowid
        for k, (kind, md) in enumerate(blocks(body)):
            db.execute("INSERT INTO book_block(sec_id,ord,kind,md) VALUES(?,?,?,?)", (sid, k, kind, md))
db.execute("INSERT INTO book_fts(book_fts) VALUES('rebuild')")

# ---- 표(CSV)와 그것을 쓰는 곳
macro = re.compile(r"@@tab\s+(.*?)@@", re.S)
used = {}
for f, _ in CHAPTERS:
    for m in macro.finditer(rd(os.path.join(ROOT, "원고", f + ".md"))):
        parts = [x.strip() for x in m.group(1).split("|")]
        used[parts[0]] = (f, parts[1], parts[2])
for p in sorted(glob.glob(os.path.join(ROOT, "표", "*.csv"))):
    name = os.path.basename(p)[:-4]; t = rd(p)
    rows = list(csv.reader(t.splitlines()))
    u = used.get(name, (None, None, None))
    db.execute("INSERT INTO book_table(name,csv_text,n_rows,n_cols,used_in,label,caption) VALUES(?,?,?,?,?,?,?)",
               (name, t, len(rows), len(rows[0]) if rows else 0, u[0], u[1], u[2]))

# ---- 그림
figm = re.compile(r"@@fig\s+(.*?)@@", re.S)
for f, _ in CHAPTERS:
    for m in figm.finditer(rd(os.path.join(ROOT, "원고", f + ".md"))):
        path, label, cap = [x.strip() for x in m.group(1).split("|", 2)]
        base = os.path.join("그림", path)
        db.execute("INSERT INTO book_figure(ch,path,label,caption,file_color,file_bw,in_chapter) VALUES(?,?,?,?,?,?,?)",
                   (path.split("/")[0], path, label, cap,
                    base + "-color.pdf" if os.path.exists(os.path.join(ROOT, base + "-color.pdf")) else None,
                    base + "-bw.pdf" if os.path.exists(os.path.join(ROOT, base + "-bw.pdf")) else None, f))

# ---- 참고문헌 → book_ref + paper
for p in sorted(glob.glob(os.path.join(ROOT, "참고문헌", "ch*.txt"))):
    ck = os.path.basename(p)[:-4]
    for l in rd(p).splitlines():
        l = l.strip()
        if not l or l.startswith("#"): continue
        ak = re.split(r"[,.\s(]", l)[0]
        ym = re.search(r"\((\d{4})", l); yr = ym.group(1) if ym else "n.d."
        plain = re.sub(r"\*", "", l)
        ex = db.execute("SELECT paper_id FROM paper WHERE apa7=?", (plain,)).fetchone()
        pid = ex[0] if ex else db.execute("INSERT INTO paper(title,authors,year,source,technique,region,apa7) VALUES(?,?,?,?,?,?,?)",
                         (plain.split("). ", 1)[-1][:200], ak, int(yr) if yr.isdigit() else None, "book-refs " + ck,
                          str(TECH[ck]) if ck in TECH else None, REGION.get(ck), plain)).lastrowid
        db.execute("INSERT INTO book_ref(ch_key,apa7,author_key,year,paper_id,verified) VALUES(?,?,?,?,?,0)", (ck, plain, ak, yr, pid))

# ---- 서지 검증 결과(참고문헌/verified-v1.csv) 반영
vf = os.path.join(ROOT, "참고문헌", "verified-v1.csv")
if os.path.exists(vf):
    for r in csv.DictReader(open(vf, encoding="utf-8")):
        db.execute("UPDATE book_ref SET verified=1 WHERE ch_key=? AND author_key=? AND year=?", (r["ch"], r["author_key"], r["year"]))
        db.execute("UPDATE paper SET doi=? WHERE paper_id IN (SELECT paper_id FROM book_ref WHERE ch_key=? AND author_key=? AND year=?)", (r["doi"], r["ch"], r["author_key"], r["year"]))

# ---- 용어, 기호, 수치
for r in list(csv.reader(rd(os.path.join(ROOT, "표", "B-terms.csv")).splitlines()))[1:]:
    db.execute("INSERT OR REPLACE INTO book_term VALUES(?,?,?)", r[:3])
for r in list(csv.reader(rd(os.path.join(ROOT, "표", "A-symbols.csv")).splitlines()))[1:]:
    db.execute("INSERT INTO book_symbol VALUES(?,?,?)", r[:3])
def flat(d, pre=""):
    for k, v in d.items():
        if isinstance(v, dict): yield from flat(v, pre + k + ".")
        else: yield pre + k, json.dumps(v, ensure_ascii=False)
for k, v in flat(json.load(open(os.path.join(ROOT, "그림/data/numbers.json"), encoding="utf-8"))):
    db.execute("INSERT INTO book_number VALUES(?,?)", (k, v))

# ---- 지역 가설
for r in list(csv.reader(rd(os.path.join(ROOT, "표", "ch02-region.csv")).splitlines()))[1:]:
    hid = r[0]; ch = {"H0": "16", "H1": "17", "H2": "18", "H3": "19"}.get(hid)
    db.execute("INSERT INTO hypothesis VALUES(?,?,?,?,?,?,?)",
               (hid, r[1], r[2], ch, 0.25, 0.7 if hid == "H0" else 0.1, "사후 확률 미산출(증거 미적재)"))

# ---- 실험 결과(run): 그림/data
SCRIPT = {"ch03": "exp-scribal.py", "ch05": "exp-slack.py", "ch07": "exp-calibration.py", "ch12": "exp-pool.py"}
for p in sorted(glob.glob(os.path.join(ROOT, "그림/data/*"))):
    fn = os.path.basename(p)
    if fn == "numbers.json": continue
    ck = fn[:4]
    body = rd(p)
    db.execute("INSERT INTO run(technique,script,script_sha256,params_json,result_json,status) VALUES(?,?,?,?,?,?)",
               (TECH.get(ck, 0), SCRIPT.get(ck, ""), "", json.dumps({"file": fn, "world": "toy(가상)"}, ensure_ascii=False),
                body if p.endswith(".json") else json.dumps({"csv": body}, ensure_ascii=False), "done"))

# ---- 지리 자료
for p in sorted(glob.glob(os.path.join(ROOT, "data/geo/*"))):
    db.execute("INSERT INTO geodata(name,path,sha256,license,attribution,retrieved_at) VALUES(?,?,?,?,?,?)",
               (os.path.basename(p), "data/geo/" + os.path.basename(p), sha(open(p, "rb").read()),
                "Public domain", "Natural Earth (naturalearthdata.com)", now))

# ---- 스킬, 개정
for p in sorted(glob.glob(os.path.join(ROOT, "스킬/*.md"))):
    t = rd(p); pdf = p[:-3] + ".pdf"
    db.execute("INSERT INTO book_skill(name,version,md_text,md_sha256,pdf_sha256) VALUES(?,?,?,?,?)",
               (os.path.basename(p)[:-3], re.search(r"v(\d+)", p).group(0) if re.search(r"v(\d+)", p) else "",
                t, sha(t.encode()), sha(open(pdf, "rb").read()) if os.path.exists(pdf) else None))
for v, s in [("v1", "초판: 8기법 장과 통합 장의 틀"), ("v2", "수식 풀이, 연구사 보강"), ("v3", "5~12장 수식 풀이, 새 쪽 시작"),
             ("v4", "2·3·4장과 서장 보강, 부록 기호표"), ("v5", "13~19장 보강(사전 등록 서식, 윌슨 구간, 사후 확률 연습, 지역별 판정표), DB 파싱 저장"),
             ("v6", "Crossref 서지 검증 반영(검증 40건, 수정 3건), verified 표시"),
             ("v12", "5~8장 각 +10만자 확장, 고문헌 실례 25건 삽입, 7장 표 캡션, 코드 강조 해제, 조판 파일 BLOB 저장, 인수인계 문서"),
             ("v13", "앞부속(표지·판권·차례), 장 여는 쪽, 마무리 장, 표 폭 자동 처리"),
             ("v16", "쪽 배치 점검(layout-check), 제목 아래 홀로 남는 줄 방지(needspace)"),
             ("v19", "표지 B안 초안: 앞표지·뒤표지 포함 단일 파일"),
             ("v20", "표지 GPU 그림(z840 ComfyUI)으로 교체"),
             ("v21", "표지 글자 크기·그림 위치 조정, 출판사 로고 삽입"),
             ("v22", "표지 그림 좌우반전(B안 확정), 뒤표지 띠 재자름"),
             ("v23", "날개 포함 펼침 표지(잠정 규격), 앞표지 1400px PNG, 518쪽 단일 파일"),
             ("v24", "스킬 v4(18절 신설), DB 일괄 저장(작업내역·스킬·표지 소스), 2쪽 보고서, 3중 백업"),
             ("prep-v3", "1권 준비편 143쪽, 그림 폭 배율 옵션, 레이아웃 점검 보완"),
             ("method-v2", "2권 방법편 474쪽, 표 7-6·8장 표 수정"),
             ("exec-v1", "3권 실행편 417쪽(9~12장 각 약 180KB, 새 그림 26개), 서문·서장·맺음말, VOLS[3], 표지 e1"),
             ("integ-v1", "4권 통합·적용편(13~19장 확장) — 작업 중")]:
    db.execute("INSERT INTO book_revision(version,rev_date,summary) VALUES(?,?,?)", (v, now if v == VERSION else None, s))
AD = os.environ.get("ASSET_DIR")
if AD:
    for dp, _, fns in os.walk(AD):
        for fn in sorted(fns):
            fp = os.path.join(dp, fn)
            if fp.endswith(".sqlite"): continue
            kind = {"pdf": "pdf", "tgz": "source", "md": "skill-md"}.get(fn.rsplit(".", 1)[-1], "file")
            db.execute("INSERT INTO book_asset(version,kind,filename,bytes,sha256,created_at,note) VALUES(?,?,?,?,?,?,?)",
                       (VERSION, kind, os.path.relpath(fp, AD), os.path.getsize(fp), sha(open(fp, "rb").read()), now, ""))

# ---- 조판 관련 전체 파일(도구, 템플릿, 지침, 자료, 인수인계, 빌드 tex/log)을 BLOB으로 저장
db.execute("""CREATE TABLE IF NOT EXISTS book_typeset_file(
  file_id INTEGER PRIMARY KEY, version TEXT, path TEXT, kind TEXT, bytes INTEGER, sha256 TEXT, content BLOB)""")
_skip = ("__pycache__", ".ppm", ".sqlite", ".png", ".pdf", ".tgz", ".zip", ".aux", ".log")
_roots = ["tools", "data", "인수인계", "표", "그림", "buildlog", "스킬", "원고", "참고문헌", "표지", "2권계획"]
_files = []
for r in _roots:
    for dp, _, fns in os.walk(os.path.join(ROOT, r)):
        if "__pycache__" in dp: continue
        for fn in sorted(fns):
            if dp.startswith(os.path.join(ROOT, "그림")) and fn.endswith(".pdf"): pass
            elif dp.startswith(os.path.join(ROOT, "buildlog")): pass
            elif fn.endswith(_skip) and not fn.endswith(("handoff-v12.pdf", "handoff-v13.pdf", "cover-front-vol1-v6b-1400px.png", "cover-v6b-front.png", "cover-v6b-strip.png", "logo-dark.pdf", "logo-light.pdf")): continue
            if "cand" in dp.split(os.sep): continue
            _files.append(os.path.join(dp, fn))
for fn in ():
    fp = os.path.join(ROOT, "build", fn)
    if os.path.exists(fp): _files.append(fp)
for fp in _files:
    b = open(fp, "rb").read(); rel = os.path.relpath(fp, ROOT)
    kind = rel.split(os.sep)[0] if os.sep in rel else "root"
    db.execute("INSERT INTO book_typeset_file(version,path,kind,bytes,sha256,content) VALUES(?,?,?,?,?,?)",
               (VERSION, rel, kind, len(b), sha(b), b))
db.execute("""CREATE TABLE IF NOT EXISTS book_build(build_id INTEGER PRIMARY KEY, version TEXT, volume TEXT, mode TEXT, pages INTEGER,
  pdf_sha256 TEXT, pdf_bytes INTEGER, overfull INTEGER, note TEXT)""")
_bj = os.path.join(ROOT, "buildlog", "builds.json")
if os.path.exists(_bj):
    for b in json.load(open(_bj, encoding="utf-8")):
        db.execute("INSERT INTO book_build(version,volume,mode,pages,pdf_sha256,pdf_bytes,overfull,note) VALUES(?,?,?,?,?,?,?,?)",
                   (b.get("version"), b.get("volume"), b.get("mode"), b.get("pages"), b.get("pdf_sha256"), b.get("pdf_bytes"), b.get("overfull"), b.get("note", "")))
print("book_build", db.execute("SELECT count(*) FROM book_build").fetchone()[0])
# ---- 서경 실제 사료·이웃 지명·학설 (data/sagyo, 원문 대조 전 자료)
_sg = os.path.join(ROOT, "data", "sagyo")
db.execute("CREATE TABLE IF NOT EXISTS sagyo_source(sid INTEGER PRIMARY KEY, kind TEXT, file TEXT, row_no INTEGER, col_json TEXT, url TEXT, verify_status TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS sagyo_note(nid INTEGER PRIMARY KEY, file TEXT, content TEXT)")
if os.path.isdir(_sg):
    for fn in sorted(os.listdir(_sg)):
        fp = os.path.join(_sg, fn)
        if fn.endswith(".csv"):
            kind = "geo" if "sagyo-geo" in fn else "neighbors" if "neighbors" in fn else "koryosa58" if "koryosa58" in fn else "theories"
            rows = list(csv.DictReader(rd(fp).splitlines()))
            for i, r in enumerate(rows, 1):
                url = r.get("출처URL") or r.get("좌표출처URL") or ""
                vs = r.get("확인상태") or r.get("대응확실도") or ""
                db.execute("INSERT INTO sagyo_source(kind,file,row_no,col_json,url,verify_status) VALUES(?,?,?,?,?,?)",
                           (kind, fn, i, json.dumps(r, ensure_ascii=False), url, vs))
        elif fn.endswith(".md"):
            db.execute("INSERT INTO sagyo_note(file,content) VALUES(?,?)", (fn, rd(fp)))
    db.execute("INSERT OR REPLACE INTO book_meta VALUES(?,?)", ("sagyo_note", "data/sagyo CSV는 에이전트가 웹 요약 도구로 수집한 1차 자료. 원문 대조 전이며 sagyo_source.verify_status를 확인할 것."))
print("sagyo_source", db.execute("SELECT kind,count(*) FROM sagyo_source GROUP BY kind").fetchall())
print("book_typeset_file", db.execute("SELECT count(*), sum(bytes) FROM book_typeset_file").fetchone())
db.execute("INSERT OR REPLACE INTO book_meta VALUES(?,?)", ("typeset_note", "조판 도구·템플릿·지침·자료·원고·빌드 tex/log가 book_typeset_file에 BLOB으로 저장됨. 복원: 각 path로 content를 쓴다."))
db.commit()
for t in ["book_chapter", "book_section", "book_block", "book_table", "book_figure", "book_ref", "paper", "run", "geodata", "book_number", "hypothesis"]:
    print(t, db.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
db.close()
