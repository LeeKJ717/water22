"""crawl-archive.py - archive.org 에 올라온 『신증동국여지승람』 스캔 항목의 메타데이터와 OCR 텍스트(djvu.txt)를 폴더 안 sqlite에 저장한다.
사용: python3 -u crawl-archive.py <출력폴더>   (z840에서 실행, 표준 라이브러리만 사용)
저장: <폴더>/db/archive.sqlite (item, afile, ocr, log), <폴더>/raw/<식별자>/ (OCR 텍스트 원본), <폴더>/SHA256SUMS
PDF·이미지 같은 큰 파일은 내려받지 않고 목록(이름·크기·해시)만 기록한다. 중단 후 재실행하면 이어받는다."""
import sys, os, json, time, hashlib, sqlite3, urllib.request, urllib.parse, datetime, subprocess
OUT = sys.argv[1]; RAW = os.path.join(OUT, "raw"); DBD = os.path.join(OUT, "db")
for p in (RAW, DBD): os.makedirs(p, exist_ok=True)
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
QUERY = "title:(新增東國輿地勝覽) OR title:(東國輿地勝覽) OR title:(신증동국여지승람) OR title:(Sinjung Tongguk yoji sungnam) OR title:(Sinjŭng Tongguk yŏji sŭngnam)"
KEYS = ["平壤", "平安道", "西京", "浿江", "大同江", "鴨綠", "箕子", "東明王"]
db = sqlite3.connect(os.path.join(DBD, "archive.sqlite"))
db.executescript("""CREATE TABLE IF NOT EXISTS item(identifier TEXT PRIMARY KEY, title TEXT, volume TEXT, date TEXT, creator TEXT, publisher TEXT, language TEXT, description TEXT, metajson TEXT, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS afile(aid INTEGER PRIMARY KEY, identifier TEXT, name TEXT, format TEXT, size INTEGER, md5 TEXT, sha1 TEXT, UNIQUE(identifier,name));
CREATE TABLE IF NOT EXISTS ocr(oid INTEGER PRIMARY KEY, identifier TEXT, name TEXT, bytes INTEGER, sha256 TEXT, rawfile TEXT, text TEXT, UNIQUE(identifier,name));
CREATE TABLE IF NOT EXISTS log(lid INTEGER PRIMARY KEY, at TEXT, action TEXT, status TEXT, detail TEXT);""")
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(a, s, d=""):
    db.execute("INSERT INTO log(at,action,status,detail) VALUES(?,?,?,?)", (now(), a, s, str(d)[:300])); db.commit()
    print(f"[{s}] {a} {str(d)[:100]}", flush=True)
def get(url, binary=False, timeout=120):
    time.sleep(1.5)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
        b = r.read(); return b if binary else b.decode("utf-8", "replace")
ids = []
try:
    d = json.loads(get("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
        {"q": QUERY, "fl[]": ["identifier"], "rows": 200, "output": "json"}, doseq=True)))
    ids = sorted(x["identifier"] for x in d["response"]["docs"]); log("search", "OK", f"{len(ids)}건")
except Exception as e:
    log("search", "ERR", e)
def s(v):
    if isinstance(v, list): return " / ".join(map(str, v))
    return "" if v is None else str(v)
for ident in ids:
    if not db.execute("SELECT 1 FROM item WHERE identifier=?", (ident,)).fetchone():
        try:
            m = json.loads(get("https://archive.org/metadata/" + ident)); md = m.get("metadata", {})
            db.execute("INSERT OR REPLACE INTO item VALUES(?,?,?,?,?,?,?,?,?,?)", (ident, s(md.get("title")), s(md.get("volume")), s(md.get("date")),
                s(md.get("creator")), s(md.get("publisher")), s(md.get("language")), s(md.get("description")), json.dumps(m, ensure_ascii=False), now()))
            for f in m.get("files", []):
                db.execute("INSERT OR IGNORE INTO afile(identifier,name,format,size,md5,sha1) VALUES(?,?,?,?,?,?)",
                           (ident, f.get("name"), f.get("format"), int(f.get("size") or 0), f.get("md5"), f.get("sha1")))
            db.commit(); log("meta " + ident, "OK", s(md.get("title")) + " | " + s(md.get("volume")))
        except Exception as e:
            log("meta " + ident, "ERR", e); continue
    # OCR 텍스트(djvu.txt 등) 저장
    for name, fmt, size in db.execute("SELECT name,format,size FROM afile WHERE identifier=? AND (name LIKE '%_djvu.txt' OR format='DjVuTXT')", (ident,)).fetchall():
        if db.execute("SELECT 1 FROM ocr WHERE identifier=? AND name=?", (ident, name)).fetchone(): continue
        try:
            b = get("https://archive.org/download/%s/%s" % (ident, urllib.parse.quote(name)), binary=True, timeout=300)
            h = hashlib.sha256(b).hexdigest(); os.makedirs(os.path.join(RAW, ident), exist_ok=True)
            rel = "raw/%s/%s" % (ident, os.path.basename(name)); open(os.path.join(OUT, rel), "wb").write(b)
            db.execute("INSERT OR IGNORE INTO ocr(identifier,name,bytes,sha256,rawfile,text) VALUES(?,?,?,?,?,?)", (ident, name, len(b), h, rel, b.decode("utf-8", "replace")))
            db.commit(); log("ocr " + ident, "OK", f"{len(b)}B")
        except Exception as e:
            log("ocr " + ident, "ERR", e)
print("==== 요약 (식별자 | 권차 | OCR바이트 | " + " ".join(KEYS) + " 출현수)", flush=True)
for ident, vol, title in db.execute("SELECT identifier,volume,title FROM item ORDER BY identifier").fetchall():
    r = db.execute("SELECT bytes,text FROM ocr WHERE identifier=?", (ident,)).fetchone()
    if r: print(ident, "|", vol, "|", r[0], "|", " ".join(str(r[1].count(k)) for k in KEYS), flush=True)
    else:
        big = db.execute("SELECT format,size FROM afile WHERE identifier=? ORDER BY size DESC LIMIT 1", (ident,)).fetchone()
        print(ident, "|", vol, "| OCR없음 | 최대파일", big, flush=True)
db.close()
subprocess.run("cd '%s' && find . -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > SHA256SUMS" % OUT, shell=True)
print("DONE", flush=True)
