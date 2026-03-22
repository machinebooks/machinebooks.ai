# Extraído de: LibroPQC/cap-17-nist-pqc.md
# Ejemplo didáctico: routes/pqc_analysis_routes.py

@pqc_bp.route('/nist-standards', methods=['GET'])
@jwt_required()
def get_nist_standards():
    """Catálogo de referencia de estándares NIST PQC."""
    return jsonify({
        'quantum_vulnerable': {
            'description': 'Algoritmos vulnerables al algoritmo de Shor',
            'algorithms': [
                {'name': 'RSA', 'status': 'quantum_vulnerable',
                 'deprecation': '2030 (NIST IR 8547)'},
                {'name': 'ECDSA', 'status': 'quantum_vulnerable',
                 'deprecation': '2030 (NIST IR 8547)'},
                {'name': 'ECDH', 'status': 'quantum_vulnerable',
                 'deprecation': '2030 (NIST IR 8547)'},
                {'name': 'DSA', 'status': 'quantum_vulnerable',
                 'deprecation': '2030 (NIST IR 8547)'},
                {'name': 'DH', 'status': 'quantum_vulnerable',
                 'deprecation': '2030 (NIST IR 8547)'},
            ],
            'pqc_alternatives': [
                'ML-KEM (FIPS 203)',
                'ML-DSA (FIPS 204)',
                'SLH-DSA (FIPS 205)',
            ]
        },
        'nist_pqc_standards': {
            'description': (
                'Estándares NIST Post-Quantum Cryptography '
                '(publicados 13 agosto 2024)'
            ),
            'algorithms': [
                {
                    'name': 'ML-KEM (Kyber)',
                    'fips': 'FIPS 203',
                    'type': 'Key Encapsulation Mechanism',
                    'usage': 'Reemplaza RSA/ECDH para intercambio de claves',
                    'variants': [
                        'ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024'
                    ],
                    'recommended': 'ML-KEM-768 para la mayoría de usos',
                },
                {
                    'name': 'ML-DSA (Dilithium)',
                    'fips': 'FIPS 204',
                    'type': 'Digital Signature',
                    'usage': 'Reemplaza RSA/ECDSA para firmas digitales',
                    'variants': [
                        'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'
                    ],
                    'recommended': 'ML-DSA-65 para equilibrio rendimiento/seguridad',
                },
                {
                    'name': 'SLH-DSA (SPHINCS+)',
                    'fips': 'FIPS 205',
                    'type': 'Stateless Hash-based Signature',
                    'usage': 'Firmas digitales (diversidad criptográfica)',
                    'variants': [
                        'SLH-DSA-SHA2-128f', 'SLH-DSA-SHAKE-256f'
                    ],
                    'recommended': 'Usar para firmware, CA roots, documentos legales',
                },
                {
                    'name': 'FALCON (FN-DSA)',
                    'fips': 'En proceso de estandarización',
                    'type': 'Digital Signature (compacta)',
                    'usage': 'Firmas compactas para certificados y DNSSEC',
                    'note': 'Firmas ~80% más pequeñas que ML-DSA',
                },
            ],
        },
        'timelines': {
            'nist_ir_8547': {
                'deprecate_classical': '2030',
                'prohibit_classical': '2035',
            },
            'cnsa_2_0': {
                'hybrid_mandatory': '2027',
                'nss_migrated': '2031-12-31',
                'hybrid_end': '2033',
                'classical_prohibited': '2035',
            },
        },
    }), 200
