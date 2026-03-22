# Extraído de: LibroBugBounty/cap-23-caso-anthropic.md
# extract_all.py -- Servidor HTTP que captura requests
# de Claude Code redirigidos via ANTHROPIC_BASE_URL

import http.server, json

class CaptureHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(length))
        # body contiene system prompt + tools
        with open("captured_request.json", "w") as f:
            json.dump(body, f, indent=2)
        # Responder con error para que Claude muestre
        # mensaje de error sin enviar datos a Anthropic
        self.send_error(500)
