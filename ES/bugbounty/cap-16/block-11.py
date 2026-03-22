# Extraído de: LibroBugBounty/cap-16-reconocimiento-surface.md
def full_security_audit(install_dir, vendor_name):
    """Auditoría de seguridad completa de una aplicación."""
    print(f"[*] Auditing {vendor_name} at {install_dir}")

    # Fase 1: Filesystem
    print("[1/3] Scanning filesystem permissions...")
    fs_findings = audit_filesystem_permissions(install_dir)
    critical_fs = [f for f in fs_findings if f["risk"] == "CRITICAL"]
    print(f"  {len(fs_findings)} findings, {len(critical_fs)} CRITICAL")

    # Fase 2: Binarios
    print("[2/3] Inventorying binaries...")
    bin_inventory = inventory_binaries(install_dir)
    print(f"  {bin_inventory['exes']} EXEs, {bin_inventory['dlls']} DLLs")
    print(f"  {len(bin_inventory['hijackable_imports'])} hijackable imports")

    # Fase 3: Servicios
    print("[3/3] Auditing services...")
    svc_findings = audit_services()
    vendor_svcs = [s for s in svc_findings
                   if vendor_name.lower() in s.get("name", "").lower()
                   or vendor_name.lower() in s.get("binary_path", "").lower()]
    print(f"  {len(vendor_svcs)} {vendor_name} services with issues")

    # Consolidar
    report = {
        "target": vendor_name,
        "install_dir": str(install_dir),
        "filesystem": {
            "total_findings": len(fs_findings),
            "critical": critical_fs,
        },
        "binaries": bin_inventory,
        "services": vendor_svcs,
    }

    # Guardar JSON para análisis con Claude
    output = Path(f"{vendor_name.lower()}_audit.json")
    with open(output, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n[+] Report saved: {output}")
    print(f"    Send to Claude for triage and attack chain analysis")

    return report
