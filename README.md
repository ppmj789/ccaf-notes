# 미지의 CCAF 노트

Claude Certified Architect - Foundations 시험 공부용 다이어리형 문제집.
Udemy 강의를 따라가며 강의 노트와 기출 문제를 한 장씩 쌓는다.

## 구조

- `pages/NNN-<q|l>-<slug>.json` — 장 하나 = 파일 하나. `q` 는 문제, `l` 은 강의 노트.
- `template.html` — 페이지 디자인과 동작. `/*__PAGES__*/` 자리에 장 데이터가 들어간다.
- `build.py` — `pages/` 를 모아 `dist/index.html` 을 만든다.
- `dist/index.html` — 완성본. 브라우저로 바로 열거나 claude.ai 아티팩트로 발행한다.

- `course.json` — Udemy 목차 정본. 섹션과 강의 번호·제목. 책 순서가 여기서 나온다.
- `serve.py` — 로컬 서버. 새로고침마다 자동 빌드하고, 답·메모를 `data/progress.json` 에 저장한다.

## 쓰는 법

```bash
python3 serve.py          # http://localhost:8787 — 새로고침할 때마다 자동 빌드
python3 build.py          # dist/index.html 만 만들고 싶을 때
```

책 구조: 표지 → 차례 → **Part 1 인강** (섹션 간지 → 강의 대본 장) → **Part 2 문제** (섹션 간지 → 문제 장).
장 추가는 `pages/` 에 JSON 을 하나 더 넣고 새로고침한다. 강의 대본은 미지가 Claude 에게 주면
Claude 가 영어 문단 + 한국어 번역 + 정리 노트 + 시험 포인트로 장을 만들어 넣는다.
claude.ai 아티팩트로도 발행할 수 있고, 그때는 답·메모가 아티팩트 서버에 저장된다.

## 어디서나 보기 (GitHub Pages + Supabase)

- `git push` 하면 `.github/workflows/pages.yml` 이 `build.py` 를 돌려 GitHub Pages 로 배포한다. 휴대폰은 그 주소로 연다.
- 답·메모는 Supabase 에 저장된다. `supabase/schema.sql` 을 SQL Editor 에서 실행하고, Authentication → Users 에서 이메일+비밀번호 사용자를 하나 만든 뒤, 프로젝트 URL 과 anon key 를 `site.json` 에 적는다.
- 페이지 오른쪽 위 `로그인` 으로 들어가면 회사·집·휴대폰이 같은 진도를 공유한다. `site.json` 이 비어 있으면 예전처럼 로컬 서버나 브라우저에만 저장한다.
- 다른 컴퓨터에서는 `git clone` 뒤 `python3 serve.py` 로 똑같이 작업하고, Claude Code 는 `CLAUDE.md` 를 읽어 같은 절차로 움직인다.

## 장 형식

공통: `id`, `kind`(`question`|`lesson`), `order`, `section`(Udemy 섹션), `lecture`(강의 번호·이름),
`title_en`, `title`(한국어), `domain`(시험 영역), `keyPoints[]`.

본문 표기 원칙: 영어가 메인, 한국어는 보조. 한 줄 안에서 ` // ` 로 나누면
앞은 크게(영어), 뒤는 작게(한국어) 표시된다. `==형광펜==`, `**굵게**`, `` `코드` ``,
`- 목록`, `### 소제목`, `| 표 |` 사용 가능.

- 문제: `question_en`, `question_ko`, `options[{key,en,ko}]`, `answer`, `explanation`, `traps[{key,why}]`
- 인강 (`kind: lesson`): `summary`(EN // KO 한두 문장), `paragraphs[{en, ko}]`(대본 문단과 한국어),
  `body`(정리 노트, 접힘), `keyPoints[]`
