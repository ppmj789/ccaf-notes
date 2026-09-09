#!/usr/bin/env python3
"""pages/*.json 을 template.html 에 심어 dist/index.html 을 만든다.

사용법: python3 build.py
- pages/ 의 JSON 은 파일명 순으로 읽고, 각 문서의 order 로 정렬한다.
- 문서에 id 가 없으면 파일명(확장자 제외)을 id 로 쓴다.
"""
import json, pathlib, sys

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
esc = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
tpl = (ROOT / 'template.html').read_text(encoding='utf-8')
assert '/*__PAGES__*/' in tpl and '/*__COURSE__*/' in tpl and '/*__SITE__*/' in tpl
out = ROOT / 'dist' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(tpl.replace('/*__PAGES__*/', esc(pages)).replace('/*__COURSE__*/', esc(course)).replace('/*__SITE__*/', esc(site)), encoding='utf-8')
print(f'{out}: {len(pages)} pages ({sum(p["kind"]=="question" for p in pages)} questions, {sum(p["kind"]=="lesson" for p in pages)} lessons)')
