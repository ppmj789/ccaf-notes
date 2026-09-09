#!/usr/bin/env python3
"""로컬 개발 서버.

- GET  /               dist/index.html (요청마다 build.py 를 다시 돌려 pages/ 변경을 바로 반영)
- GET  /api/ping       {"ok": true, "claude": <claude CLI 사용 가능 여부>}
- GET  /api/data       {"progress": {...}, "lectures": [...]}
- POST /api/progress   {"id": pageId, "data": {...}}      → data/progress.json
- POST /api/lecture    {doc}                             → data/lectures/<id>.json
- POST /api/lecture/delete {"id": ...}
- POST /api/sample     {"prompt": "...", "model": "haiku"} → {"text": "..."} (claude -p 로 실행)

사용법: python3 serve.py [포트]   (기본 8787)
"""
import json, os, pathlib, shutil, subprocess, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).parent.resolve()
DIST = ROOT / 'dist'
DATA = ROOT / 'data'
LECTURES = DATA / 'lectures'
PROGRESS = DATA / 'progress.json'
CLAUDE = shutil.which('claude')


def build():
    subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True, capture_output=True)


def read_json(p, default):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return default


def write_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(p)


def run_claude(prompt, model='haiku'):
    if not CLAUDE:
        raise RuntimeError('claude CLI 를 찾을 수 없습니다')
    env = {k: v for k, v in os.environ.items() if k not in ('CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT')}
    r = subprocess.run([CLAUDE, '-p', '--model', model], input=prompt, text=True,
                       capture_output=True, cwd=str(ROOT), env=env, timeout=600)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or '').strip()[:800] or f'claude exit {r.returncode}')
    return r.stdout.strip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(DIST), **kw)

    def log_message(self, fmt, *args):
        if not str(args[0]).startswith(('GET /api/ping', 'GET /favicon')):
            super().log_message(fmt, *args)

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n).decode('utf-8') or '{}')

    def do_GET(self):
        if self.path == '/api/ping':
            return self.send_json({'ok': True, 'claude': bool(CLAUDE)})
        if self.path == '/api/data':
            lectures = [read_json(p, None) for p in sorted(LECTURES.glob('*.json'))]
            return self.send_json({'progress': read_json(PROGRESS, {}), 'lectures': [l for l in lectures if l]})
        if self.path in ('/', '/index.html'):
            try:
                build()
            except subprocess.CalledProcessError as e:
                msg = (e.stderr or e.stdout or b'').decode('utf-8', 'replace')
                body = f'<meta charset="utf-8"><pre>build.py 실패\n\n{msg}</pre>'.encode('utf-8')
                self.send_response(500); self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
                return
        return super().do_GET()

    def end_headers(self):
        if self.path.endswith('.html') or self.path in ('/', ''):
            self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_POST(self):
        try:
            body = self.read_body()
            if self.path == '/api/progress':
                prog = read_json(PROGRESS, {})
                prog[body['id']] = body['data']
                write_json(PROGRESS, prog)
                return self.send_json({'ok': True})
            if self.path == '/api/lecture':
                doc = body
                if not doc.get('id'):
                    return self.send_json({'error': 'id 없음'}, 400)
                write_json(LECTURES / f"{doc['id']}.json", doc)
                return self.send_json({'ok': True})
            if self.path == '/api/lecture/delete':
                p = LECTURES / f"{body['id']}.json"
                if p.exists():
                    p.unlink()
                return self.send_json({'ok': True})
            if self.path == '/api/sample':
                text = run_claude(body['prompt'], body.get('model') or 'haiku')
                return self.send_json({'text': text})
            return self.send_json({'error': 'unknown endpoint'}, 404)
        except Exception as e:  # noqa: BLE001
            return self.send_json({'error': str(e)}, 500)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    build()
    print(f'미지의 CCAF 노트 → http://localhost:{port}   (claude CLI: {"있음" if CLAUDE else "없음"})')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
