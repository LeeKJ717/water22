# 부록 C 증거 DB 스키마와 재현 절차 {-}

## 이 부록의 길잡이 {-}

**이 부록은 무엇인가.** 4장에서 설명한 증거 DB의 정확한 설계와, 이 책의 계산을 다시 돌리는 절차를 모은 곳이다. 직접 계산을 재현해 보려는 독자를 위한 부록이다.

**어떻게 쓰나.** 읽기만 할 독자는 건너뛰어도 된다. 재현하려면 C.1(스키마)로 표와 열을 확인하고, C.2(환경)로 필요한 프로그램을 갖추고, C.3(재현 절차)을 순서대로 따라 한다. C.4와 C.5는 DB에 자료를 적재하는 도구와 판 관리 규칙을 설명한다.

## C.1 스키마 {-}

DB는 SQLite이며 스키마 파일은 `placeloc-schema-v1.sql`이다. 표와 열은 4장의 표 4-1과 같다. 주요 제약은 다음과 같다.

- `coord`의 모든 행은 좌표와 함께 `basis`(gazetteer, survey, estimate)를 가진다.
- `evidence`는 `source_text`와 `place`를 외래키로 참조한다. 출처 없는 증거는 들어갈 수 없다.
- `source_text.verified`가 0인 구절은 본문에 따옴표로 인용하지 않는다.

## C.2 환경 {-}

- 계산: Python 3.12, `numpy`, `scipy`, `networkx`, `matplotlib`, `shapely`, `rasterio`, `hanja`
- 조판: pandoc, XeLaTeX, Noto CJK KR 글꼴
- 지리 자료: Natural Earth 1:10m(공공 도메인), Copernicus DEM GLO-90

## C.3 재현 절차 {-}

1. 라이브러리 시험: `python3 tools/test-placeloc.py`. 모든 단위 시험과 보정 시험(가상 세계 120개에서 95% 영역의 적중률 0.88 이상)이 통과해야 한다.
2. 실험: `exp-calibration.py`(7장), `exp-scribal.py`(3장), `exp-slack.py`(5장), `exp-pool.py`(12장)가 `그림/data/`에 결과를 쓴다.
3. 수치: `calc-numbers.py`가 본문에 쓰이는 수치를 `numbers.json`에 모으고, `mk-tables.py`가 표를 만든다. 본문은 `\{\{키\}\}`로 수치를 참조하므로 수치를 손으로 옮겨 적지 않는다.
4. 그림: `figs-a.py`, `figs-b.py`, `figs-c.py`.
5. 조판: `python3 tools/build.py color` 및 `bw`. 컬러판과 흑백판을 각각 만든다.

## C.4 DB 적재 도구 {-}

외부 자료를 DB에 적재하는 수집 도구는 `tools/collect/`에 있다. 집필 환경이 외부 사이트에 접근할 수 없었으므로, 이 도구들은 연구용 컴퓨터에서 실행하도록 작성되었다.

- `collect-papers.py`: 선행 논문을 OpenAlex에서 모아 메타데이터, 초록, 공개 PDF(있을 때)와 본문을 `paper` 표에 넣는다.
- `verify-refs.py`: 각 장의 참고문헌 파일을 Crossref에 조회하여 실재 여부와 서지 일치도를 CSV로 낸다. **참고문헌 목록의 모든 항목은 이 검증을 거친 뒤에 확정한다.**
- `collect-sources.py`: 위키문헌 같은 공개 원문에서 지정한 문서를 가져와 `source_text`에 `verified=0`으로 넣는다.
- `collect-coords.py`: Wikidata에서 지명의 좌표를 출처와 함께 가져와 `coord`에 `basis='gazetteer'`로 넣는다.

## C.5 판 관리 {-}

책은 판마다 번호를 붙이고(`v1`, `v2`), 판이 바뀌면 `run` 표에 어느 DB 상태에서 만든 판인지 해시를 남긴다. 사료가 추가되어 수치가 바뀌면 이전 판은 지우지 않는다.
