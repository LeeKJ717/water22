-- 책 원고 파싱 저장용 스키마 v1 (placeloc-schema-v1.sql 위에 추가)
-- 수정 권위: book_section.body_md. book_block은 검색·점검용 파생 색인이며 import 때 다시 만든다.
CREATE TABLE book_meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE book_chapter (
  ch_id INTEGER PRIMARY KEY, file TEXT UNIQUE NOT NULL, ord INTEGER, part_title TEXT,
  title TEXT, ref_key TEXT, n_chars INTEGER, md_sha256 TEXT
);
CREATE TABLE book_section (
  sec_id INTEGER PRIMARY KEY, ch_id INTEGER REFERENCES book_chapter(ch_id),
  ord INTEGER, level INTEGER, heading TEXT,
  body_md TEXT NOT NULL,          -- 제목 줄을 포함한 원문. 절을 이어 붙이면 원고 파일이 된다
  n_chars INTEGER
);
CREATE TABLE book_block (
  block_id INTEGER PRIMARY KEY, sec_id INTEGER REFERENCES book_section(sec_id),
  ord INTEGER, kind TEXT,         -- para/list/math/quote/fig/tab/refs/code/heading
  md TEXT
);
CREATE TABLE book_table (
  tbl_id INTEGER PRIMARY KEY, name TEXT UNIQUE, csv_text TEXT, n_rows INTEGER, n_cols INTEGER,
  used_in TEXT, label TEXT, caption TEXT
);
CREATE TABLE book_figure (
  fig_id INTEGER PRIMARY KEY, ch TEXT, path TEXT, label TEXT, caption TEXT,
  file_color TEXT, file_bw TEXT, in_chapter TEXT
);
CREATE TABLE book_ref (
  ref_id INTEGER PRIMARY KEY, ch_key TEXT, apa7 TEXT, author_key TEXT, year TEXT,
  paper_id INTEGER REFERENCES paper(paper_id), verified INTEGER DEFAULT 0
);
CREATE TABLE book_term (term TEXT PRIMARY KEY, english TEXT, meaning TEXT);
CREATE TABLE book_symbol (symbol TEXT, reading TEXT, meaning TEXT);
CREATE TABLE book_number (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE hypothesis (
  hyp_id TEXT PRIMARY KEY, region TEXT, status TEXT, chapter TEXT,
  prior_equal REAL, prior_conservative REAL, note TEXT
);
CREATE TABLE book_asset (
  asset_id INTEGER PRIMARY KEY, version TEXT, kind TEXT, filename TEXT, bytes INTEGER,
  sha256 TEXT, created_at TEXT, note TEXT
);
CREATE TABLE book_skill (
  skill_id INTEGER PRIMARY KEY, name TEXT, version TEXT, md_text TEXT, md_sha256 TEXT, pdf_sha256 TEXT
);
CREATE TABLE book_revision (
  rev_id INTEGER PRIMARY KEY, version TEXT, rev_date TEXT, summary TEXT
);
CREATE VIRTUAL TABLE book_fts USING fts5(heading, body_md, content='book_section', content_rowid='sec_id', tokenize='trigram');
