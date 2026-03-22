# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_scanner.py

def scan_kms(self, session: boto3.Session, region: str):
    """Escanea claves KMS buscando problemas criptográficos"""
    try:
        kms = session.client('kms')
        paginator = kms.get_paginator('list_keys')

        for page in paginator.paginate():
            for key in page.get('Keys', []):
                key_id = key['KeyId']
                self.resources_scanned += 1

                try:
                    key_info = kms.describe_key(KeyId=key_id)['KeyMetadata']

                    # Ignorar claves gestionadas por AWS (no controlables)
                    if key_info.get('KeyManager') == 'AWS':
                        continue

                    # Comprobar estado de la clave
                    if key_info.get('KeyState') == 'PendingDeletion':
                        self._add_finding(
                            'kms-key-pending-deletion', key_id,
                            key_info.get('Arn'), 'kms', 'key', region
                        )

                    # Comprobar rotación automática
                    try:
                        rotation = kms.get_key_rotation_status(KeyId=key_id)
                        if not rotation.get('KeyRotationEnabled', False):
                            self._add_finding(
                                'kms-key-rotation-disabled', key_id,
                                key_info.get('Arn'), 'kms', 'key', region
                            )
                    except Exception:
                        pass  # Algunas claves no soportan rotación

                except Exception as e:
                    logger.debug(f"Error checking key {key_id}: {e}")

    except Exception as e:
        logger.error(f"Error scanning KMS in {region}: {e}")
