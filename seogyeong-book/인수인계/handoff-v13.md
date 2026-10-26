# 인수인계 v13 — 《고려 서경(西京)의 위치를 추정하다》 1권 방법편

작성 기준: 책 버전 v24 (2026-10-23)

## 1. 현재 상태
- 1권 구조 완성: 앞부속(표지·판권·차례), 장 여는 쪽, 마무리 장, 표지(앞·뒤·날개), 표지 포함 단일 파일 518쪽(표지 1 + 본문 516 + 뒤표지 1).
- 최신 산출물: book-vol1-v23-{color,bw}-with-cover.pdf, cover-spread-vol1-v4-wings-provisional.pdf, cover-front-vol1-v6b-1400px.png.
- 표지: z840 ComfyUI(Z-Image-Turbo) 그림 s01_s3_749845655, B안(좌우반전), 출판사 로고 포함.

## 2. 빌드 방법
- 본문: `BOOK_VERSION=vNN VOLUME=1 python3 tools/build.py color|bw`
- 표지: 표지/cover-v6b.tex (xelatex 두 번), 펼침: 표지/spread-v3.tex
- 합본: pypdf로 기존 with-cover 파일의 첫·끝 쪽 교체
- DB: `BOOK_VERSION=v24 ASSET_DIR=<산출물> python3 tools/mk-db.py build/placeloc-v24.sqlite`

## 3. 미완료 (증거 기준)
1. 아직 확장하지 않은 장: 00~04, 09~15, 17~19, 부록
2. 실제 서경 사료·좌표·결과 (현재 실험은 가상 세계 toy)
3. 원문 대조 필요: RE01, RE28, RE29
4. 서지 일부 미검증, 02장 "조선 초" 문장 재확인
5. 판권: ISBN, 정가, 발행일 미정
6. POD 규격(날개 폭 70mm, 책등 28.9mm, 재단 여유 3mm)은 잠정값 — 인쇄소 확정 후 교체
7. 저자 소개 문구 확인, 표지 그림 업스케일
8. 2권 집필 시작(차례: 2권계획/vol2-toc-v1.md)
9. geonames-book 표지 재디자인 여부(이박사님 결정 대기)

## 4. 작업 규칙
증거 기준·"원문 대조 필요" 표기·중2 눈높이·왼쪽 제본 여백·APA 7·파일명에 구분자 없음·버전 표기.
스킬: 스킬/seogyeong-skill-v4.md (18절 표지·POD 규칙)
