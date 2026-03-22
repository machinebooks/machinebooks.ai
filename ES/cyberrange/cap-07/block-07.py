# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: traffic-profiles/corporate-dns.py
# Genera tráfico DNS realista para ejercicios de detección

from scapy.all import *
import random
import time

# Dominios legítimos comunes en una red corporativa
DOMAINS = [
    "mail.ejemplo-corp.local",
    "intranet.ejemplo-corp.local",
    "fileserver.ejemplo-corp.local",
    "updates.ejemplo-corp.local",
    "vpn.ejemplo-corp.local",
    "erp.ejemplo-corp.local",
    "crm.ejemplo-corp.local",
]

# Dominios sospechosos (para que el blue team los detecte)
SUSPICIOUS = [
    "c2.malware-ejemplo.xyz",
    "exfil.badactor-ejemplo.tk",
]

def generate_dns_traffic(iface: str, duration: int = 300):
    """Generar tráfico DNS durante N segundos."""
    end_time = time.time() + duration

    while time.time() < end_time:
        # 95% tráfico legítimo, 5% sospechoso
        if random.random() < 0.95:
            domain = random.choice(DOMAINS)
        else:
            domain = random.choice(SUSPICIOUS)

        pkt = (
            IP(dst="10.100.0.1")  # DNS del gateway
            / UDP(dport=53)
            / DNS(rd=1, qd=DNSQR(qname=domain))
        )
        send(pkt, iface=iface, verbose=0)

        # Intervalo aleatorio entre consultas (0.1-2 segundos)
        time.sleep(random.uniform(0.1, 2.0))

if __name__ == "__main__":
    generate_dns_traffic("eth0", duration=600)
