# -*- coding: utf-8 -*-
import http.server
import socketserver
import urllib.request
import urllib.parse
import sys
import os

PORT = 8888
DIRECTORY = "HuyCa_Web"

class ProxyServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/proxy'):
            self.handle_proxy('GET')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/proxy'):
            self.handle_proxy('POST')
        else:
            self.send_error(501, "Unsupported method")

    def handle_proxy(self, method):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        target_url = params.get('url', [None])[0]
        if not target_url:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"Missing url parameter"}')
            return

        body = None
        if method == 'POST':
            content_len = int(self.headers.get('Content-Length', 0))
            if content_len > 0:
                body = self.rfile.read(content_len)

        try:
            req = urllib.request.Request(target_url, data=body, method=method)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
            req.add_header('Accept', '*/*')
            
            # Forward custom headers (FreeReels, Range, Content-Type, Authorization, etc.)
            for k, v in self.headers.items():
                lk = k.lower()
                if lk not in ['host', 'origin', 'referer', 'content-length', 'user-agent', 'accept-encoding']:
                    req.add_header(k, v)
            req.add_header('Accept-Encoding', 'identity')

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                
                # Auto decompress if upstream still compressed with gzip
                if resp.headers.get('Content-Encoding') == 'gzip' or (len(data) >= 2 and data[:2] == b'\x1f\x8b'):
                    import gzip
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass

                self.send_response(resp.status)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.send_header('Content-Length', str(len(data)))
                for k, v in resp.headers.items():
                    if k.lower() in ['content-type', 'content-range', 'accept-ranges']:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), ProxyServerHandler) as httpd:
        print(f"Serving HuyCa_Web with API proxy on port {PORT}")
        httpd.serve_forever()
