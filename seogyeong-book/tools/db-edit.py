"""db-edit.py - DB에 파싱 저장된 원고를 보고, 고치고, 원고 파일로 내보낸다.
  python3 tools/db-edit.py DB list [장]            장·절 목록(번호 포함)
  python3 tools/db-edit.py DB get 장 절번호         절 본문 출력
  python3 tools/db-edit.py DB put 장 절번호 파일    파일 내용으로 절을 교체(제목 줄 포함)
  python3 tools/db-edit.py DB find 검색어           절 본문 전문 검색
  python3 tools/db-edit.py DB export 출력폴더        모든 장을 원고 md로 복원
  python3 tools/db-edit.py DB verify                복원본이 원고 폴더의 파일과 같은지 확인
장 인자는 파일 이름 앞부분(예: 13-compare 또는 13)."""
import sys, os, sqlite3, hashlib
db = sqlite3.connect(sys.argv[1]); cmd = sys.argv[2]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def chap(a):
    r = db.execute("SELECT ch_id,file FROM book_chapter WHERE file=? OR file LIKE ?", (a, a + "-%")).fetchone()
    if not r: sys.exit("장 없음: " + a)
    return r
def text(ch_id):
    return "".join(r[0] for r in db.execute("SELECT body_md FROM book_section WHERE ch_id=? ORDER BY ord", (ch_id,)))
if cmd == "list":
    q = "SELECT c.file,s.ord,s.level,s.heading,s.n_chars FROM book_section s JOIN book_chapter c USING(ch_id)"
    a = ()
    if len(sys.argv) > 3: q += " WHERE c.ch_id=?"; a = (chap(sys.argv[3])[0],)
    for f, o, lv, h, n in db.execute(q + " ORDER BY c.ord,s.ord", a): print(f"{f}\t{o}\t{'#'*lv} {h}\t{n}자")
elif cmd == "get":
    cid, _ = chap(sys.argv[3]); print(db.execute("SELECT body_md FROM book_section WHERE ch_id=? AND ord=?", (cid, int(sys.argv[4]))).fetchone()[0], end="")
elif cmd == "put":
    cid, _ = chap(sys.argv[3]); new = open(sys.argv[5], encoding="utf-8").read()
    db.execute("UPDATE book_section SET body_md=?,n_chars=? WHERE ch_id=? AND ord=?", (new, len(new), cid, int(sys.argv[4])))
    db.execute("INSERT INTO book_fts(book_fts) VALUES('rebuild')"); db.commit(); print("교체 완료. export 후 build.py 실행")
elif cmd == "find":
    for f, o, h in db.execute("SELECT c.file,s.ord,s.heading FROM book_fts f JOIN book_section s ON s.sec_id=f.rowid JOIN book_chapter c USING(ch_id) WHERE book_fts MATCH ?", ('"' + sys.argv[3] + '"',)): print(f, o, h)
elif cmd == "export":
    out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    for cid, f in db.execute("SELECT ch_id,file FROM book_chapter ORDER BY ord"):
        open(os.path.join(out, f + ".md"), "w", encoding="utf-8").write(text(cid))
    print("내보냄:", out)
elif cmd == "verify":
    bad = 0
    for cid, f in db.execute("SELECT ch_id,file FROM book_chapter ORDER BY ord"):
        a = open(os.path.join(ROOT, "원고", f + ".md"), encoding="utf-8").read()
        if a != text(cid): bad += 1; print("불일치:", f)
    print("불일치", bad)
