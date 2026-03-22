# Extraído de: LibroBugBounty/cap-24-caso-sunshine.md
req = urllib.request.Request(
    "https://localhost:47990/api/apps",
    headers=headers
)
with urllib.request.urlopen(req, context=ctx) as resp:
    apps = json.loads(resp.read())
    for app in apps.get("apps", []):
        print(f"  - {app.get('name')}: {app.get('cmd', 'N/A')}")

# Resultado:
#   - Desktop: (sin comando)
#   - Steam Big Picture: steam://open/bigpicture
