-- placeloc-db 스키마 v1 (SQLite). 서경 지명 추정서의 사료·좌표·논문·계산 이력 저장용
PRAGMA foreign_keys = ON;

-- 논문(선행연구): 전문과 PDF 원본을 함께 저장
CREATE TABLE paper (
  paper_id INTEGER PRIMARY KEY,
  doi TEXT, title TEXT NOT NULL, authors TEXT, year INTEGER, journal TEXT,
  abstract TEXT, fulltext TEXT, pdf_blob BLOB, pdf_sha256 TEXT,
  source TEXT,                 -- 수집 경로(OpenAlex, Crossref 등)
  technique TEXT,              -- 기법 번호 1~8 (복수는 쉼표)
  region TEXT,                 -- 한반도/요하/산동/만주
  apa7 TEXT,                   -- APA 7판 참고문헌 문자열
  added_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 사료(원문): 인용은 원문 대조 후 verified=1
CREATE TABLE source_text (
  src_id INTEGER PRIMARY KEY,
  work TEXT NOT NULL,          -- 서명(고려사, 삼국사기, 요사 등)
  juan TEXT, passage TEXT,     -- 권·조목
  original TEXT NOT NULL,      -- 원문(한문)
  reading_ko TEXT,             -- 한국 한자음 독음
  translation_ko TEXT,
  edition TEXT,                -- 저본·판본
  verified INTEGER DEFAULT 0, verified_note TEXT
);

-- 지명(시대별 이름 포함)
CREATE TABLE place (
  place_id INTEGER PRIMARY KEY,
  name_han TEXT NOT NULL, name_ko TEXT,   -- 한자, 한국 한자음
  pinyin_cmp TEXT,                        -- 비교용 병음(본문 괄호용)
  era TEXT, kind TEXT,                    -- 시대, 성·산·강·주 등
  note TEXT
);
CREATE TABLE place_alias (
  alias_id INTEGER PRIMARY KEY,
  place_id INTEGER REFERENCES place(place_id),
  name_han TEXT, name_ko TEXT, era_from TEXT, era_to TEXT, src_id INTEGER REFERENCES source_text(src_id)
);

-- 좌표: 지명 사전에서 받은 값만 넣고 출처 필수
CREATE TABLE coord (
  coord_id INTEGER PRIMARY KEY,
  place_id INTEGER REFERENCES place(place_id),
  lon REAL NOT NULL, lat REAL NOT NULL,
  sigma_km REAL,                          -- 불확실성(1 시그마, km)
  basis TEXT,                             -- gazetteer/survey/estimate
  gazetteer TEXT, gazetteer_id TEXT, url TEXT, retrieved_at TEXT
);

-- 증거: 사료에서 뽑은 제약(거리·방위·경유·포함 관계)
CREATE TABLE evidence (
  ev_id INTEGER PRIMARY KEY,
  src_id INTEGER REFERENCES source_text(src_id),
  place_id INTEGER REFERENCES place(place_id),
  ev_type TEXT,                -- distance/bearing/contains/adjacent/route/phonetic
  ref_place_id INTEGER REFERENCES place(place_id),
  value_lo REAL, value_hi REAL, unit TEXT,  -- 구간(예: 리(里)→km 환산 전후 모두 기록)
  weight REAL, note TEXT
);

-- 기법별 계산 실행 이력(재현성)
CREATE TABLE run (
  run_id INTEGER PRIMARY KEY,
  technique INTEGER NOT NULL,  -- 1~8
  target_place_id INTEGER REFERENCES place(place_id),
  script TEXT, script_sha256 TEXT, params_json TEXT,
  result_json TEXT,            -- 중심, 신뢰영역, 기법별 지표
  started_at TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT
);

-- 지리 자료와 라이선스
CREATE TABLE geodata (
  geo_id INTEGER PRIMARY KEY,
  name TEXT, path TEXT, sha256 TEXT, license TEXT, attribution TEXT, retrieved_at TEXT
);

CREATE INDEX idx_paper_tech ON paper(technique);
CREATE INDEX idx_evidence_place ON evidence(place_id);
CREATE INDEX idx_coord_place ON coord(place_id);
