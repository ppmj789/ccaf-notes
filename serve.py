#!/usr/bin/env python3
"""로컬 개발 서버.

- GET  /               dist/index.html (요청마다 build.py 를 다시 돌려 pages/ 변경을 바로 반영)
- GET  /api/ping       {"ok": true}
- GET  /api/data       {"progress": {...}}
- POST /api/progress   {"id": pageId, "data": {...}}      → data/progress.json

사용법: python3 serve.py [포트]   (기본 8787)
"""
import json, pathlib, subprocess, sys, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).parent.resolve()
DIST = ROOT / 'dist'
DATA = ROOT / 'data'
PROGRESS = DATA / 'progress.json'
LOCK = threading.Lock()  # 드릴이 여러 문제를 한꺼번에 저장할 때 tmp 파일 경합 방지


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
            return self.send_json({'ok': True})
        if self.path == '/api/data':
            return self.send_json({'progress': read_json(PROGRESS, {})})
        if self.path in ('/', '/index.html', '/drill/', '/drill/index.html'):
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
                with LOCK:
                    prog = read_json(PROGRESS, {})
                    prog[body['id']] = body['data']
                    write_json(PROGRESS, prog)
                return self.send_json({'ok': True})
            return self.send_json({'error': 'unknown endpoint'}, 404)
        except Exception as e:  # noqa: BLE001
            return self.send_json({'error': str(e)}, 500)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    build()
    print(f'미지의 CCAF 노트 → http://localhost:{port}')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
