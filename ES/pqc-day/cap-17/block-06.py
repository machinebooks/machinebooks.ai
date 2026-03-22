# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: patrones/report_nist_section.py

def generate_nist_compliance_section(findings: list, report) -> None:
    """Genera la sección de cumplimiento NIST PQC del informe PDF."""

    # Contar hallazgos por algoritmo vulnerable
    vuln_counts = {}
    for f in findings:
        algo = f.get('algorithm', 'Unknown')
        vuln_counts[algo] = vuln_counts.get(algo, 0) + 1

    # Tabla de mapeo hallazgo -> estándar NIST destino
    migration_map = {
        'RSA': ('FIPS 203 / FIPS 204', 'ML-KEM / ML-DSA'),
        'ECDSA': ('FIPS 204', 'ML-DSA'),
        'ECDH': ('FIPS 203', 'ML-KEM'),
        'DH': ('FIPS 203', 'ML-KEM'),
        'DSA': ('FIPS 204 / FIPS 205', 'ML-DSA / SLH-DSA'),
    }

    # Generar tabla en el PDF
    report.add_heading('Referencia de estándares NIST PQC')
    report.add_paragraph(
        'Los siguientes estándares fueron publicados como documentos '
        'finales el 13 de agosto de 2024 y constituyen la referencia '
        'de migración para todos los hallazgos de este informe.'
    )

    for algo, count in sorted(vuln_counts.items(), key=lambda x: -x[1]):
        if algo in migration_map:
            fips, pqc_algo = migration_map[algo]
            report.add_table_row([
                f'{algo} ({count} hallazgos)',
                fips,
                pqc_algo,
                'Deprecado 2030 / Prohibido 2035 (NIST IR 8547)',
            ])

    # Sección de plazos regulatorios
    report.add_heading('Plazos regulatorios aplicables', level=2)
    report.add_timeline([
        ('2027', 'CNSA 2.0: esquemas híbridos obligatorios para NSS'),
        ('2030', 'NIST IR 8547: depreciar RSA/ECC clásico'),
        ('2031', 'CNSA 2.0: sistemas NSS completamente migrados'),
        ('2033', 'CNSA 2.0: fin de esquemas híbridos'),
        ('2035', 'NIST IR 8547: prohibir criptografía asimétrica clásica'),
    ])
