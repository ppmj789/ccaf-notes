#!/usr/bin/env python3
"""pages/*.json 을 template.html 에 심어 dist/index.html 을 만들고,
문제(pages 의 q + bank/)·patterns.json·exam.json 을 drill.html 에 심어 dist/drill/index.html 을 만든다.

사용법: python3 build.py
- pages/ 의 JSON 은 파일명 순으로 읽고, 각 문서의 order 로 정렬한다.
- 문서에 id 가 없으면 파일명(확장자 제외)을 id 로 쓴다.
- bank/ 의 변형 문제는 드릴에만 들어간다(노트 책에는 안 나옴).
- 드릴의 테마 CSS(:root 팔레트)는 template.html 에서 잘라 와 한 곳에서만 관리한다.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
pages = []
for f in sorted((ROOT / 'pages').glob('*.json')):
    d = json.loads(f.read_text(encoding='utf-8'))
    d.setdefault('id', f.stem)
    for k in ('kind', 'title', 'order'):
        if k not in d:
            sys.exit(f'{f.name}: {k} 필드가 없습니다')
    if d['kind'] == 'question':
        keys = [o['key'] for o in d.get('options', [])]
        if d.get('answer') not in keys:
            sys.exit(f'{f.name}: answer {d.get("answer")!r} 가 options 에 없습니다')
    pages.append(d)
pages.sort(key=lambda d: d['order'])
ids = [p['id'] for p in pages]
if len(ids) != len(set(ids)):
    sys.exit('id 중복: ' + ', '.join(i for i in ids if ids.count(i) > 1))

course = json.loads((ROOT / 'course.json').read_text(encoding='utf-8')) if (ROOT / 'course.json').exists() else {'sections': []}
known = {s['title'] for s in course['sections']}
for p in pages:
    sec = p.get('section') or 'Unsorted'
    if sec not in known and sec != 'Unsorted':
        print(f'경고: {p["id"]} 의 section "{sec}" 이 course.json 에 없습니다 (책 끝에 Unsorted 로 감)')

site = json.loads((ROOT / 'site.json').read_text(encoding='utf-8')) if (ROOT / 'site.json').exists() else {}
import base64, mimetypes
for cov in sorted((ROOT / 'assets').glob('cover.*')) if (ROOT / 'assets').exists() else []:
    mime = mimetypes.guess_type(cov.name)[0] or 'image/jpeg'
    site['cover'] = f'data:{mime};base64,' + base64.b64encode(cov.read_bytes()).decode('ascii')
    break
esc = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
tpl = (ROOT / 'template.html').read_text(encoding='utf-8')
assert '/*__PAGES__*/' in tpl and '/*__COURSE__*/' in tpl and '/*__SITE__*/' in tpl
out = ROOT / 'dist' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(tpl.replace('/*__PAGES__*/', esc(pages)).replace('/*__COURSE__*/', esc(course)).replace('/*__SITE__*/', esc(site)), encoding='utf-8')

# PWA: 아이콘과 manifest 를 dist 로 (휴대폰 홈 화면 아이콘)
ICONS = ['icon-192.png', 'icon-512.png', 'apple-touch-icon.png']
manifest = {
    'name': '미지의 CCAF 노트',
    'short_name': 'CCAF 노트',
    'description': 'Claude Certified Architect - Foundations 공부 노트',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'orientation': 'portrait',
    'background_color': '#7CC924',
    'theme_color': '#7CC924',
    'lang': 'ko',
    'icons': [
        {'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
        {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'},
    ],
}
for name in ICONS:
    srcp = ROOT / 'assets' / name
    if srcp.exists():
        (out.parent / name).write_bytes(srcp.read_bytes())
    else:
        print(f'경고: assets/{name} 이 없습니다 (PWA 아이콘 빠짐)')
(out.parent / 'manifest.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'{out}: {len(pages)} pages ({sum(p["kind"]=="question" for p in pages)} questions, {sum(p["kind"]=="lesson" for p in pages)} lessons)')

# ---------- drill (문제풀이) ----------
patterns = json.loads((ROOT / 'patterns.json').read_text(encoding='utf-8')) if (ROOT / 'patterns.json').exists() else []
exam = json.loads((ROOT / 'exam.json').read_text(encoding='utf-8')) if (ROOT / 'exam.json').exists() else {}
pids = {p['id'] for p in patterns}
bank = []
for f in sorted((ROOT / 'bank').glob('*.json')) if (ROOT / 'bank').exists() else []:
    d = json.loads(f.read_text(encoding='utf-8'))
    d.setdefault('id', 'b-' + f.stem); d.setdefault('kind', 'question'); d.setdefault('generated', True)
    keys = [o['key'] for o in d.get('options', [])]
    if d.get('answer') not in keys:
        sys.exit(f'{f.name}: answer {d.get("answer")!r} 가 options 에 없습니다')
    bank.append(d)
questions = [p for p in pages if p['kind'] == 'question'] + bank
for q in questions:
    if not q.get('patternId'):
        print(f'경고: {q["id"]} 에 patternId 가 없습니다 (패턴 사전에 안 묶임)')
    elif q['patternId'] not in pids:
        print(f'경고: {q["id"]} 의 patternId "{q["patternId"]}" 가 patterns.json 에 없습니다')
qids = [q['id'] for q in questions]
if len(qids) != len(set(qids)):
    sys.exit('문제 id 중복: ' + ', '.join(i for i in qids if qids.count(i) > 1))
if (ROOT / 'drill.html').exists():
    drill_tpl = (ROOT / 'drill.html').read_text(encoding='utf-8')
    m = re.search(r'(  :root \{.*?color-scheme: dark; \}\n)', tpl, re.S)
    theme = m.group(1) if m else ''
    for k in ('/*__THEME_CSS__*/', '/*__QUESTIONS__*/', '/*__PATTERNS__*/', '/*__EXAM__*/', '/*__SITE__*/'):
        assert k in drill_tpl, f'drill.html 에 {k} 가 없습니다'
    dsite = {k: v for k, v in site.items() if k != 'cover'}
    dout = ROOT / 'dist' / 'drill' / 'index.html'
    dout.parent.mkdir(parents=True, exist_ok=True)
    dout.write_text(drill_tpl.replace('/*__THEME_CSS__*/', theme).replace('/*__QUESTIONS__*/', esc(questions)).replace('/*__PATTERNS__*/', esc(patterns)).replace('/*__EXAM__*/', esc(exam)).replace('/*__SITE__*/', esc(dsite)), encoding='utf-8')
    print(f'{dout}: {len(questions)} questions ({len(bank)} from bank), {len(patterns)} patterns')
