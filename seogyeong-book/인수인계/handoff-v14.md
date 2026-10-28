# 서경 책 시리즈 현황·인수인계 v1 (2026-10-26)

책: 《고려 서경(西京)의 위치를 추정하다: 여덟 가지 방법으로 동아시아 고전 지명을 좌표로 옮기기》 (이광조, 과학과영성출판사). 집필은 2026-10-26 현재 중지 상태.

## 1. 시리즈 구조 (4권, 장 번호는 전체에서 연속)
| 권 | 이름 | 내용 | 상태 |
|---|---|---|---|
| 1권 | 준비편 | 서장 + 1~4장(사료, 학설사, 사료 비판, 증거 DB) + 맺음말 + 부록 C | v2 완성본 143쪽(표지 포함) |
| 2권 | 방법편 | 5~8장(여덟 방법 중 네 가지: 제약, 지오레퍼런싱, 베이즈, 최소비용경로) + 맺음말 + 부록 A·B | v2 474쪽(표지 포함) |
| 3권 | 실행편 | 9~12장 + 도구·GPU | 미착수(2권 서문에 예고만) |
| 4권 | 통합·적용편 | 13~19장 | 미착수 |

## 2. 저장 위치
- 완성본 PDF(노트북): ~/Downloads 와 ~/Desktop/daily3/seogyeong-book/pdf/
  - book-vol1-prep-v2-color/bw-with-cover.pdf, book-vol2-method-v2-color/bw-with-cover.pdf, cover-vol1-prep-v1.pdf, cover-vol2-method-v1.pdf
- 원고·도구·그림 원본: GitHub LeeKJ717/water22, 브랜치 seogyeong-book, 폴더 seogyeong-book/ (main 브랜치의 웹사이트는 건드리지 않음). PDF·build·DEM(60MB)·표지 gpu 폴더는 제외.
- 클라우드 작업 폴더: /home/claude/book (세션 종료 시 사라질 수 있음). 빌드: BOOK_VERSION=<표시> VOLUME=<1|2> python3 tools/build.py color|bw
- DB: placeloc-v27.sqlite.gz (약 34MB, 20MB 두 조각 seogyeongdbv27part00/01). 복원: cat part* > x.gz; gunzip x.gz. 장·절·블록·표·그림·참고문헌·숫자·개정이력(book_revision)이 들어 있음.
- 백업: z840 ~/seogyeongbackup/prepv2 → z440 ~/backup/seogyeong/prepv2 → NAS /mnt/nas/seogyeong/prepv2

## 3. 지켜 온 규칙
근거 없는 출처·인용·숫자 금지(원문 대조 필요 표시), 가상 사례는 표시하고 서경 결과로 쓰지 않음, 중2 수준, APA 7, 장 첫쪽 대표 그림+소차례, 장 끝 수식 풀이, 왼쪽 철 여백, 한국 한자음.

## 4. 남은 작업
1. 레이아웃: 1권 지도 쪽(fig02-1-regions) 오른쪽 약 4mm 초과, 2권 269쪽 경고(그림 선), 2권 overfull hbox 24건, 표 칸 두 줄 꺾임 전수 점검, 그림 글자 크기 점검.
2. 1권 3장 31쪽(목표 25~28쪽) 축약 검토.
3. 중복: 2권 서문·서장이 1권과 문단 단위로 겹침(7개 문단, ch00-map 표 동일) — 줄이거나 1권 참조로 돌림. 같은 사료 한 줄(□里四尺, E12)이 1권 3장, 2권 7·8장에 반복.
4. 3권(9~12장)·4권(13~19장) 집필, 실제 서경 사료·좌표 적재, "원문 대조 필요" 목록 정리.
5. 출판: ISBN, 정가, 발행일, 날개 포함 펼침 표지(POD 규격), geonames-book(다른 책)과 표지 날개 상호 소개.
6. 문서: 2권계획/volume-plan-v2.md를 4권·연속 장 번호 결정에 맞게 개정.
7. 한 권이 마무리될 때마다: GitHub 올림 → 완성본은 노트북 폴더 → 3중 백업(z840→z440→NAS) → DB 갱신.
