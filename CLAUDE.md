# 미지의 CCAF 노트 — 작업 절차 (Claude 용)

이 폴더는 박미지의 Claude Certified Architect - Foundations(CCAF) 시험 공부 노트 프로젝트다.
Udemy 강의 대본과 기출 문제를 "한 장씩 넘기는 다이어리" 웹페이지로 쌓는다.
**사용자가 대본이나 문제를 주면 아래 절차를 매번 똑같이 수행한다.** 사용자 응답은 항상 한국어.

## 구조

- `course.json` — Udemy 목차 정본 (`sections[{no, title, lectures[{no, title}]}]`). 책 순서가 여기서 나온다. 섹션 `no` 는 Udemy 섹션 번호(사용자는 섹션 1·2 를 노트 없이 들었으므로 3부터 시작). 없으면 순서대로 매긴다.
- `pages/NNN-l-<slug>.json` — 인강 장 (강의 하나 = 파일 하나). `NNN` 은 강의 번호 3자리.
- `pages/NNN-q-<slug>.json` — 문제 장. `NNN` 은 소속 강의 번호, 뒤에 `-1`, `-2` 로 구분.
- `template.html` — 디자인과 동작. `build.py` 가 `pages/` + `course.json` 을 심어 `dist/index.html` 을 만든다.
- `serve.py` — 로컬 서버 (`python3 serve.py` → http://localhost:8787, 새로고침마다 자동 빌드). 답·메모는 `data/progress.json`.
- 아티팩트(claude.ai): https://claude.ai/code/artifact/f38187b9-3a04-4fc3-a0db-c20d1fff34de — `dist/index.html` 을 이 `url` 로 재발행, capabilities `{"db": {}}` 만.
- `assets/cover.jpg` — 표지 삽화(Higgsfield 로 생성, 720px). build 가 data URI 로 `site.cover` 에 심고 표지가 쓴다. 표지는 토익 문제집 레이아웃(시리즈 띠 · 큰 제목 · 섹션 블록 + 삽화 · 이름/진도 · 하단 PART 띠).
- `site.json` — Supabase 접속 정보(`supabaseUrl`, `supabaseAnonKey`). build 가 `/*__SITE__*/` 에 심는다. anon key 는 공개용이라 커밋해도 된다. 진도 저장 우선순위: 아티팩트 db → Supabase(로그인 필요, `supabase/schema.sql` 의 `progress` 테이블, RLS 로 본인 행만) → 로컬 serve.py → localStorage.
- GitHub: https://github.com/ppmj789/ccaf-notes (공개, 기본 브랜치 `master`). `.github/workflows/pages.yml` 이 push 마다 build 해서 GitHub Pages 로 배포 → https://ppmj789.github.io/ccaf-notes/ (휴대폰은 이 주소). Pages 환경 허용 브랜치에 `master` 를 추가해 두었다.

책 구조: 표지 → 차례 → **Part 1 인강**(섹션 간지 → 강의 장) → **Part 2 문제**(섹션 간지 → 문제 장). 인강과 문제는 섞지 않는다.

## 표기 원칙 (사용자 지시, 바꾸지 말 것)

- **영어가 메인, 한국어는 보조.** 본문·keyPoints·summary·examTrends 는 `English // 한국어` 형식. 페이지가 ` // ` 로 나눠 영어 크게, 한국어 작게 그린다.
- **대본은 한 줄씩.** 문단으로 합치지 않는다. 사용자가 인강을 보면서 자막 한 줄에 대응하는 영어 한 줄 + 밑의 한국어 한 줄을 읽는다.
- 기술 용어·식별자(JSON, schema, tool_use, tool_choice, enum, null …)는 한국어 줄에서도 영어 그대로.
- 자동 자막 오타 교정: `Clod`→`Claude`, `Shop assist`→`ShopAssist`, `Cloud`(모델을 뜻할 때)→`Claude`.
- 마크업: `==형광펜==`(노란 형광펜), `**굵게**`(파란 펜 글씨), `__밑줄__`(빨간 펜 밑줄), `((상자))`(빨간 펜 네모, 짧은 구절에만), `` `코드` ``, `- 목록`, `### 소제목`(청록 형광펜 띠), `| 표 |`.
- 이모지 쓰지 않는다. 한국어 개행은 단어 단위(template 이 `word-break: keep-all`).

## 대본을 받았을 때 — 인강 장 만들기

입력: 섹션 이름, 강의 번호·제목, Transcript 전체. (섹션·번호가 없으면 물어보되, 대본 작업은 먼저 진행.)

1. `course.json` 에 섹션·강의가 없으면 추가한다. 섹션 제목은 Udemy 표기 그대로, 섹션 `no` 는 정수, 강의 `no` 는 문자열.
2. `pages/NNN-l-<slug>.json` 을 만든다. 필드:
   - `id`: `l-NNN`, `kind`: `lesson`, `order`: 강의 번호(정수), `section`, `lecture`(문자열 번호)
   - `title_en`, `title`(한국어 제목), `domain`(시험 영역: 모델 선택 · 프롬프트·평가 · 툴·에이전트 루프 · 지식·RAG · 멀티에이전트 · Claude Code · 신뢰성)
   - `summary`: 두 문장. `English // 한국어`
   - `paragraphs`: `[{"en": "...", "ko": "..."}, ...]` — **대본 줄 하나당 한 항목.** 사용자가 붙여 넣은 줄바꿈을 그대로 따른다. 줄바꿈이 없거나 문단으로 뭉쳐 왔으면 문장·절 단위(8~18 단어)로 나누고 구두점을 복원한다. 내용 누락·병합 금지. 한국어는 직접 번역한다(자연스럽고 짧게).
   - `body`: 정리 노트. `### 소제목` 4~7개, 각 `- ` 목록 2~5줄, 줄마다 `English // 한국어`. 핵심 구절 `==형광펜==`. 페이지에서 접힌 상태로 표시된다.
   - `keyPoints`: 시험에서 기억할 한 줄 3~5개, `English // 한국어`. 노란 포스트잇.
   - `examTrends`: 시험 경향 분석. 분홍 포스트잇. 각 문장 `English // 한국어`.
     - `how`: 이 주제가 시험에 어떤 형태(시나리오·정의·비교)로 나오는지, 정답이 보통 어떤 구조인지
     - `answerLooks[]`: 정답 보기에 등장하는 문구·조합 2~4개
     - `traps[]`: 오답 보기 패턴 3~4개 (왜 오답인지 한 문장)
     - `memorize`: 한 줄 암기 문장
   - `createdAt`: ISO 시각
3. 채팅으로도 답한다: 강의 요약 → 핵심 개념 풀이(사용자가 CCAF 초심자이니 쉬운 말로) → 시험 경향 한 단락.
4. 빌드·검증·발행·커밋 (아래).

## 문제를 받았을 때 — 문제 장 만들기

입력: 영어 문제, 보기, 정답 (+ 소속 강의). 먼저 채팅으로 문제·정답을 한국어로 해석하고 왜 정답인지, 오답 보기가 왜 틀렸는지 설명한다. 그다음:

- `pages/NNN-q-<slug>.json`: `id` `q-NNN-k`, `kind` `question`, `order` = 강의번호 + 0.1k (예 24.1), `section`, `lecture`, `title_en`, `title`, `domain`,
  `question_en`, `question_ko`, `options[{key, en, ko}]`, `answer`, `explanation`(한국어 위주, 지문 단서 ↔ 정답 문구 짝짓기, `==형광펜==`, 표 가능), `traps[{key, why}]`, `keyPoints[]`, `pattern`, `createdAt`.
  - **지문·보기 형광펜**: `question_en` 과 각 `options[].en` 의 키워드를 `==…==` 로 감싼다(지문 4~8곳, 보기마다 1~3곳). 페이지가 영어 지문을 문장 단위로 잘라 ①②③ 번호를 붙이므로 형광펜은 한 문장 안에서만 닫는다.
  - **`pattern`** (지문 분석, 접힘 칸): `type`(문제 유형 한 구절), `asks`(실제로 묻는 것 한 줄), `clues[{text, means}]`(지문 키워드 → 그것이 뜻하는 바, 3~5개, means 는 빨간 펜 주석처럼 짧게), `answerShape`(정답 보기의 구조), `distractorShape`(오답 보기의 구조). 모두 한국어.
- 소속 강의를 모르면 `section: "Unsorted"`, `lecture: ""` 로 두고 사용자에게 묻는다.

## 빌드 · 검증 · 발행 · 커밋 (매번)

```bash
cd ~/ccaf-notes
python3 build.py                       # 필드 검증 포함. 경고가 나오면 고친다.
node -e "const fs=require('fs');const s=fs.readFileSync('dist/index.html','utf8');new Function(s.match(/<script>([\s\S]*)<\/script>/)[1]);console.log('JS_OK')"
```

- 로컬 서버가 안 떠 있으면: `(setsid nohup python3 serve.py 8787 > /tmp/ccaf-server.log 2>&1 &)`. 재시작 시 `pgrep -f "^python3 serve.py"` 로 PID 를 찾아 kill (`pkill -f` 는 자기 셸까지 죽이니 금지).
- 아티팩트 재발행: Artifact 툴에 `file_path=~/ccaf-notes/dist/index.html`, `url=위 주소`, capabilities 는 생략(유지) 또는 `{"db": {}}`.
- 커밋: `git add -A && git commit -m "<무엇을 추가했는지 한국어 한 줄>"` (사용자 이름 Miji). 원격 `origin`(GitHub) 이 있으면 `git push` 까지 한다. push 가 곧 배포다.

## 디자인 변경 시

`template.html` 만 고친다. **정갈한 필기 노트** 느낌이 정체성이다(세로 A4 판형·영어|한국어 두 칸·코넬 노트는 사용자가 써 보고 뺀 것이니 다시 넣지 않는다. 영어 위·한국어 아래, 가로 꽉 채우기): 모눈 종이(상단 `테마` 선택으로 종이[기본]·화이트 노트·민트·미드나잇 팔레트, `:root[data-palette]` 변수 세트, localStorage `ccaf-palette`), 정자체(Gowun Dodum 본문·Gowun Batang 제목·IBM Plex Mono 코드), 제목에 파스텔 형광펜 띠(소제목 청록, 핵심 정리 노랑, 시험 경향 주황, Why 주황, Traps 분홍), 파란 펜(굵게·번호·소제목 라벨)과 빨간 펜(밑줄·상자·별표·✗), 왼쪽 링 제본, 페이지 위쪽 가로 인덱스 탭(표지·차례·인강·문제 — 인강·문제 탭은 그 파트의 한 줄짜리 목록 페이지로 감). **장난스러운 손글씨체(Gaegu 등)·기울어진 포스트잇·낙서·회전 요소는 사용자가 뺀 것이니 다시 넣지 않는다.** 인강 장 구성: 제목 옆 `요약 보기 ↓` 버튼 → Summary → 대본(접기·펴기, 마지막 상태를 localStorage 에 기억) 한 줄씩 → `핵심 정리`(`대본으로 ↑` 버튼, 정리 노트 접힘, Exam points 빨간 별 목록, 시험 경향 ✓/✗ 와 `외우기` 빨간 상자). 문제 장 구성: 영어 지문 문장 번호 ①②③ + 형광펜 → `지문 분석` 접힘 칸 → 보기(형광펜) → 풀이. 인강 장에는 메모 textarea 가 없다(문제 장에만). 탭 이름은 하는 일이 드러나게. 진행 상태 표시(진도)·자신감 도장·페이지 내 AI 기능은 사용자가 뺀 것이니 다시 넣지 않는다.