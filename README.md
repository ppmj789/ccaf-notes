# 미지의 CCAF 노트

Claude Certified Architect - Foundations 시험 공부용 다이어리형 문제집.
Udemy 강의를 따라가며 강의 노트와 기출 문제를 한 장씩 쌓는다.

## 구조

- `pages/NNN-<q|l>-<slug>.json` — 장 하나 = 파일 하나. `q` 는 문제, `l` 은 강의 노트.
- `template.html` — 페이지 디자인과 동작. `/*__PAGES__*/` 자리에 장 데이터가 들어간다.
- `build.py` — `pages/` 를 모아 `dist/index.html` 을 만든다.
- `dist/index.html` — 완성본. 브라우저로 바로 열거나 claude.ai 아티팩트로 발행한다.

- `serve.py` — 로컬 서버. 페이지를 띄우고, 답·메모·대본을 `data/` 에 파일로 저장하고,
  번역·요약은 이 컴퓨터의 Claude Code CLI(`claude -p`)로 만든다.
- `data/lectures/<id>.json` — 인강 듣기 탭에서 저장한 대본과 한국어 번역·요약.
- `data/progress.json` — 문제 답과 메모 (gitignore).

## 쓰는 법

```bash
python3 serve.py          # http://localhost:8787 — 새로고침할 때마다 자동 빌드
python3 build.py          # dist/index.html 만 만들고 싶을 때
```

장 추가는 `pages/` 에 JSON 을 하나 더 넣고 새로고침한다.
claude.ai 아티팩트로도 발행할 수 있고, 그때는 답·메모·대본이 아티팩트 서버에, 번역은 페이지 안 Claude 로 된다.

## 장 형식

공통: `id`, `kind`(`question`|`lesson`), `order`, `section`(Udemy 섹션), `lecture`(강의 번호·이름),
`title_en`, `title`(한국어), `domain`(시험 영역), `keyPoints[]`.

본문 표기 원칙: 영어가 메인, 한국어는 보조. 한 줄 안에서 ` // ` 로 나누면
앞은 크게(영어), 뒤는 작게(한국어) 표시된다. `==형광펜==`, `**굵게**`, `` `코드` ``,
`- 목록`, `### 소제목`, `| 표 |` 사용 가능.

- 문제: `question_en`, `question_ko`, `options[{key,en,ko}]`, `answer`, `explanation`, `traps[{key,why}]`
- 강의 노트: `summary`(EN // KO 한두 문장), `body`
