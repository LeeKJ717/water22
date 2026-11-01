"""mk-db-ext.py - mk-db.py 가 만든 seogyeong.sqlite 에 '2판·수정 작업용' 확장 표를 추가한다.
사용: python3 mk-db-ext.py <seogyeong.sqlite> [--root 조판루트] [--pdf-dir PDF폴더] [--crawl-dir 크롤폴더들의 상위폴더] [--no-blob]
추가되는 것(모두 DB 안에서 조회·수정 가능, 여러 번 실행해도 같은 결과):
  book_volume, book_volume_chapter   권(1~4)별 구성: 어느 장이 몇 권 몇 번째인지, 서문 파일
  book_aux_md                        장 목록에 없는 보조 원고(p0-preface, notes 등)
  book_cite                          본문 인용(저자, 연도) ↔ 참고문헌(book_ref) 연결, 못 찾은 것은 matched=0
  book_flag                          '원문 대조 필요'·'확인하지 못'·가상·실례 표시 문장 목록(status 로 2판 처리 상태 관리)
  book_numuse, book_figuse           본문이 쓰는 수치 키({{키}})와 그림 라벨
  book_pdf (+ book_asset)            완성 PDF 등록(해시·쪽수·권·판·컬러/흑백), 권별 최신판은 BLOB 까지 보관
  crawl_<db>_<표>                    크롤 폴더들의 sqlite 를 label(폴더 이름) 열을 붙여 통째로 복사
  source_text                        크롤한 사료 전문(위키문헌 전사본)을 사료 원문표에 적재(verified=0)
  paper_fetch                        참고문헌별 DOI/URL 주소와 논문 전문 수집 상태(todo) - 전문 수집기의 작업 목록
  v_flag_open, v_cite_unmatched, v_volume_toc   자주 쓰는 조회 뷰"""
import logging; logging.disable(logging.CRITICAL)
import sys, os, re, ast, glob, sqlite3, hashlib, argparse, datetime, json
ap = argparse.ArgumentParser()
ap.add_argument("db"); ap.add_argument("--root"); ap.add_argument("--pdf-dir"); ap.add_argument("--crawl-dir"); ap.add_argument("--no-blob", action="store_true")
A = ap.parse_args()
ROOT = A.root or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
db = sqlite3.connect(A.db)
now = datetime.datetime.now().isoformat(timespec="seconds")
def rd(p): return open(p, encoding="utf-8").read()
def sha(b): return hashlib.sha256(b).hexdigest()
stats = {}
def done(k, n): stats[k] = n; print(f"{k:28s} {n}", flush=True)
db.executescript("""
CREATE TABLE IF NOT EXISTS import_log(at TEXT, kind TEXT, label TEXT, table_name TEXT, rows INTEGER);
CREATE TABLE IF NOT EXISTS book_volume(volume TEXT PRIMARY KEY, title TEXT, preface_file TEXT, ref_keys TEXT);
CREATE TABLE IF NOT EXISTS book_volume_chapter(volume TEXT, ord INTEGER, ch_id INTEGER, file TEXT, role TEXT, PRIMARY KEY(volume, ord));
CREATE TABLE IF NOT EXISTS book_aux_md(file TEXT PRIMARY KEY, md TEXT, sha256 TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS book_cite(cite_id INTEGER PRIMARY KEY, block_id INTEGER, sec_id INTEGER, ch_id INTEGER, author_key TEXT, year TEXT, ref_id INTEGER, matched INTEGER);
CREATE TABLE IF NOT EXISTS book_flag(flag_id INTEGER PRIMARY KEY, block_id INTEGER, sec_id INTEGER, ch_id INTEGER, kind TEXT, sentence TEXT, status TEXT DEFAULT 'open', note TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS book_numuse(block_id INTEGER, sec_id INTEGER, key TEXT);
CREATE TABLE IF NOT EXISTS book_figuse(block_id INTEGER, sec_id INTEGER, label TEXT);
CREATE TABLE IF NOT EXISTS book_pdf(pdf_id INTEGER PRIMARY KEY, filename TEXT UNIQUE, kind TEXT, volume TEXT, mode TEXT, version TEXT, with_cover INTEGER, bytes INTEGER, sha256 TEXT, pages INTEGER, is_latest INTEGER, content BLOB);
CREATE TABLE IF NOT EXISTS paper_fetch(paper_id INTEGER PRIMARY KEY, doi TEXT, url TEXT, kind TEXT, status TEXT DEFAULT 'todo', pdf_sha256 TEXT, fetched_at TEXT, note TEXT);
""")
# ---- A. 권별 구성
src = rd(os.path.join(ROOT, "tools", "build.py"))
m = re.search(r"^VOLS = (\{.*?\n\})\n", src, re.S | re.M)
VOLS = ast.literal_eval(m.group(1)) if m else {}
chid = {f: i for i, f in db.execute("SELECT ch_id,file FROM book_chapter")}
db.execute("DELETE FROM book_volume"); db.execute("DELETE FROM book_volume_chapter")
for v, (chs, title, pre, refs) in sorted(VOLS.items()):
    db.execute("INSERT INTO book_volume VALUES(?,?,?,?)", (v, title, pre, ",".join(refs)))
    db.execute("INSERT INTO book_volume_chapter VALUES(?,?,?,?,?)", (v, 0, chid.get(pre), pre, "preface"))
    for i, f in enumerate(chs, 1):
        db.execute("INSERT INTO book_volume_chapter VALUES(?,?,?,?,?)", (v, i, chid.get(f), f, "chapter"))
done("book_volume", len(VOLS))
db.execute("DELETE FROM book_aux_md"); n = 0
for p in sorted(glob.glob(os.path.join(ROOT, "원고", "*.md"))):
    f = os.path.basename(p)[:-3]
    if f in chid: continue
    t = rd(p); db.execute("INSERT INTO book_aux_md VALUES(?,?,?,?)", (f, t, sha(t.encode()), "장 목록(CHAPTERS)에 없는 보조 원고")); n += 1
done("book_aux_md", n)
# ---- B. 인용 연결 / C. 표시 문장 / D. 수치·그림 사용
refmap = {}
for rid, ck, ak, y in db.execute("SELECT ref_id,ch_key,author_key,year FROM book_ref"): refmap.setdefault((ck, ak, y), rid)
refany = {}
for (ck_, ak_, y_), rid_ in refmap.items(): refany.setdefault((ak_, y_), rid_)
chkey = {c: k for c, k in db.execute("SELECT ch_id,ref_key FROM book_chapter")}
CITE = re.compile(r"([A-Z][A-Za-z'’\-]+)(?: et al\.| & [A-Z][A-Za-z'’\-]+)?[,\s]*\(?(\d{4})[a-z]?\)?")
FLAGS = [("verify", re.compile(r"원문 대조 필요")), ("unchecked", re.compile(r"확인하지 못")), ("virtual", re.compile(r"가상(?:의)?\s*(?:예|사례|자료|수치|데이터|값|입력)|\(가상|가상 예시")),
         ("real-example", re.compile(r"<!--\s*real-example"))]
NUM = re.compile(r"\{\{([A-Za-z0-9_.가-힣]+)(?::[^}]+)?\}\}"); FIG = re.compile(r"@@fig\s+(.*?)@@", re.S)
for t in ("book_cite", "book_flag", "book_numuse", "book_figuse"): db.execute(f"DELETE FROM {t}")
nc = nm = nf = nn = nu = 0
rows = db.execute("SELECT b.block_id,b.sec_id,s.ch_id,b.kind,b.md FROM book_block b JOIN book_section s ON s.sec_id=b.sec_id").fetchall()
for bid, sid, cid, kind, md in rows:
    if kind in ("para", "list", "quote"):
        for name, y in set(CITE.findall(md)):
            ck = chkey.get(cid); rid = refmap.get((ck, name, y)) if ck else None
            if rid is None: rid = refany.get((name, y))
            if rid or 1900 <= int(y) <= 2030:
                db.execute("INSERT INTO book_cite(block_id,sec_id,ch_id,author_key,year,ref_id,matched) VALUES(?,?,?,?,?,?,?)", (bid, sid, cid, name, y, rid, 1 if rid else 0))
                nc += 1; nm += 1 if rid else 0
    sents = [x.strip() for x in re.split(r"(?<=[.。!?])\s+|\n", md) if x.strip()]
    for fk, rx in FLAGS:
        if fk == "real-example":
            if rx.search(md): db.execute("INSERT INTO book_flag(block_id,sec_id,ch_id,kind,sentence,updated_at) VALUES(?,?,?,?,?,?)", (bid, sid, cid, fk, md[:300], now)); nf += 1
            continue
        for s in sents:
            if rx.search(s):
                db.execute("INSERT INTO book_flag(block_id,sec_id,ch_id,kind,sentence,updated_at) VALUES(?,?,?,?,?,?)", (bid, sid, cid, fk, s[:500], now)); nf += 1
    for k in set(NUM.findall(md)): db.execute("INSERT INTO book_numuse VALUES(?,?,?)", (bid, sid, k)); nn += 1
    for fm in FIG.finditer(md):
        parts = [x.strip() for x in fm.group(1).split("|", 2)]
        if len(parts) >= 2: db.execute("INSERT INTO book_figuse VALUES(?,?,?)", (bid, sid, parts[1])); nu += 1
done("book_cite", nc); done("book_cite matched", nm); done("book_flag", nf); done("book_numuse", nn); done("book_figuse", nu)
# ---- E. PDF 등록
def verkey(name):
    m2 = re.search(r"-v(\d+)([a-z]?)", name); return (int(m2.group(1)), m2.group(2)) if m2 else (0, "")
if A.pdf_dir and os.path.isdir(A.pdf_dir):
    try:
        from pypdf import PdfReader
    except Exception:
        PdfReader = None
    db.execute("DELETE FROM book_pdf"); db.execute("DELETE FROM book_asset WHERE kind='pdf'")
    items = []
    for p in sorted(glob.glob(os.path.join(A.pdf_dir, "*.pdf"))):
        n = os.path.basename(p); vm = re.search(r"vol(\d)", n)
        kind = "cover" if n.startswith("cover") else "book" if n.startswith(("book-", "seogyeong-book")) else "doc"
        vol = vm.group(1) if vm else ("1" if kind == "book" else None)
        mode = "bw" if re.search(r"-bw", n) else "color" if re.search(r"-color", n) else None
        b = open(p, "rb").read(); pages = None
        if PdfReader:
            try: pages = len(PdfReader(p).pages)
            except Exception: pass
        items.append(dict(n=n, kind=kind, vol=vol, mode=mode, ver="v%d%s" % verkey(n), wc=int("with-cover" in n or "합본" in n), b=b, pages=pages, mt=os.path.getmtime(p)))
    latest = {}
    for it in items:
        if it["kind"] == "book" and it["wc"] and it["vol"] and it["mode"]: latest[(it["kind"], it["vol"], it["mode"])] = max(latest.get((it["kind"], it["vol"], it["mode"]), it), it, key=lambda x: verkey(x["n"]))
        if it["kind"] == "cover" and it["vol"]: latest[("cover", it["vol"], "")] = max(latest.get(("cover", it["vol"], ""), it), it, key=lambda x: verkey(x["n"]))
    lat = {id(v) for v in latest.values()}; nb = 0
    for it in items:
        isl = 1 if id(it) in lat else 0; blob = it["b"] if (isl and not A.no_blob) else None; nb += 1 if blob else 0
        db.execute("INSERT INTO book_pdf(filename,kind,volume,mode,version,with_cover,bytes,sha256,pages,is_latest,content) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (it["n"], it["kind"], it["vol"], it["mode"], it["ver"], it["wc"], len(it["b"]), sha(it["b"]), it["pages"], isl, blob))
        db.execute("INSERT INTO book_asset(version,kind,filename,bytes,sha256,created_at,note) VALUES(?,?,?,?,?,?,?)",
                   (it["ver"], "pdf", it["n"], len(it["b"]), sha(it["b"]), datetime.datetime.fromtimestamp(it["mt"]).isoformat(timespec="seconds"), f"{it['kind']} vol={it['vol']} mode={it['mode']}"))
    done("book_pdf", len(items)); done("book_pdf blob(latest)", nb)
# ---- F. 크롤 DB 통째로 복사
if A.crawl_dir and os.path.isdir(A.crawl_dir):
    db.commit(); ncp = 0
    for d in sorted(glob.glob(os.path.join(A.crawl_dir, "*"))):
        label = os.path.basename(d)
        for f in sorted(glob.glob(os.path.join(d, "db", "*.sqlite"))):
            stem = re.sub(r"\W", "_", os.path.splitext(os.path.basename(f))[0])
            db.execute("ATTACH DATABASE ? AS c", (f,))
            for (tb,) in db.execute("SELECT name FROM c.sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
                t = f"crawl_{stem}_{tb}"
                if db.execute("SELECT 1 FROM import_log WHERE kind='crawl' AND label=? AND table_name=?", (label, t)).fetchone():
                    db.execute("DELETE FROM %s WHERE label=?" % t, (label,)); db.execute("DELETE FROM import_log WHERE kind='crawl' AND label=? AND table_name=?", (label, t))
                try:
                    if not db.execute("SELECT 1 FROM main.sqlite_master WHERE name=?", (t,)).fetchone():
                        db.execute(f"CREATE TABLE {t} AS SELECT '' AS label, * FROM c.{tb} WHERE 0")
                    db.execute(f"INSERT INTO {t} SELECT ?, * FROM c.{tb}", (label,))
                    n = db.execute(f"SELECT count(*) FROM {t} WHERE label=?", (label,)).fetchone()[0]
                    db.execute("INSERT INTO import_log VALUES(?,?,?,?,?)", (now, "crawl", label, t, n)); ncp += n
                except Exception as e:
                    print("크롤 복사 실패", label, tb, e)
            db.commit(); db.execute("DETACH DATABASE c")
    done("crawl rows copied", ncp)
    # ---- G. 사료 원문표 적재
    db.execute("DELETE FROM source_text WHERE edition LIKE '위키문헌%'"); ns = 0; seen = set()
    def has(t): return db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (t,)).fetchone()
    if has("crawl_sagyocrawl_page"):
        for lab, tg, site, title, fa, text in db.execute("SELECT label,target,site,title,fetched_at,text FROM crawl_sagyocrawl_page WHERE text IS NOT NULL").fetchall():
            if (tg, title, sha(text.encode())) in seen: continue
            seen.add((tg, title, sha(text.encode())))
            db.execute("INSERT INTO source_text(work,juan,passage,original,edition,verified,verified_note) VALUES(?,?,?,?,?,?,?)",
                       (tg, title, "전문", text, f"위키문헌({site}) 전사본 {str(fa)[:10]} [{lab}]", 0, "사이트 전사본. 원문 대조 필요")); ns += 1
    if has("crawl_yeoji_page"):
        for lab, title, fa, text in db.execute("SELECT label,title,fetched_at,text FROM crawl_yeoji_page").fetchall():
            if ("yj", title, sha(text.encode())) in seen: continue
            seen.add(("yj", title, sha(text.encode())))
            db.execute("INSERT INTO source_text(work,juan,passage,original,edition,verified,verified_note) VALUES(?,?,?,?,?,?,?)",
                       ("新增東國輿地勝覽", title.split("/")[-1], "전문", text, f"위키문헌(zh) 전사본 {str(fa)[:10]} [{lab}]", 0, "사이트 전사본. 원문 대조 필요")); ns += 1
    done("source_text", ns)
# ---- H. 논문 전문 수집 작업 목록
db.execute("DELETE FROM paper_fetch WHERE status='todo'"); nh = 0
for pid, doi, apa in db.execute("SELECT paper_id,doi,apa7 FROM paper").fetchall():
    if db.execute("SELECT 1 FROM paper_fetch WHERE paper_id=?", (pid,)).fetchone(): continue
    um = re.search(r"https?://[^\s)\]>]+", apa or ""); url = um.group(0).rstrip(".,;") if um else None
    dm = re.search(r"10\.\d{4,9}/[^\s)\]>]+", (doi or "") + " " + (apa or "")); d2 = dm.group(0).rstrip(".,;") if dm else None
    kind = "doi" if d2 else "web" if url else "none"
    db.execute("INSERT INTO paper_fetch(paper_id,doi,url,kind) VALUES(?,?,?,?)", (pid, d2, url, kind)); nh += 1
done("paper_fetch", nh)
for k, n in db.execute("SELECT kind,count(*) FROM paper_fetch GROUP BY kind").fetchall(): print(f"  paper_fetch {k}: {n}")
# ---- I. 뷰
db.executescript("""
DROP VIEW IF EXISTS v_flag_open; CREATE VIEW v_flag_open AS SELECT f.flag_id,f.kind,c.file AS chapter,s.heading,f.sentence,f.note FROM book_flag f JOIN book_chapter c ON c.ch_id=f.ch_id JOIN book_section s ON s.sec_id=f.sec_id WHERE f.status='open';
DROP VIEW IF EXISTS v_cite_unmatched; CREATE VIEW v_cite_unmatched AS SELECT c.file AS chapter,x.author_key,x.year,x.block_id FROM book_cite x JOIN book_chapter c ON c.ch_id=x.ch_id WHERE x.matched=0;
DROP VIEW IF EXISTS v_volume_toc; CREATE VIEW v_volume_toc AS SELECT v.volume,v.title AS volume_title,vc.ord,vc.role,vc.file,c.title AS chapter_title,c.n_chars FROM book_volume v JOIN book_volume_chapter vc ON vc.volume=v.volume LEFT JOIN book_chapter c ON c.ch_id=vc.ch_id ORDER BY v.volume,vc.ord;
""")
db.execute("INSERT OR REPLACE INTO book_meta(key,value) VALUES('ext_version','ext-v1 ' || ?)", (now,))
db.commit(); db.execute("VACUUM"); db.close()
print("확장 끝:", json.dumps(stats, ensure_ascii=False))
