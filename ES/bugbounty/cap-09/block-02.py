# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
known_cve_ioctls = {
    0x222400, 0x222404, 0x222408,  # CVE-2023-39780
    0x22240C, 0x222410, 0x222414,  # CVE-2022-36438
}

cve_found = known_cve_ioctls & set(found.keys())
if cve_found:
    print(f"[!] KNOWN CVE IOCTLs PRESENT: {[hex(c) for c in cve_found]}")
