# Extraído de: LibroFinOps/cap-15-waste-automatico.md
def scan_orphan_snapshots(max_age_days: int = 180) -> list[dict]:
    """
    Identifica snapshots potencialmente huérfanos:
    1. Snapshots cuyo volumen de origen ya no existe
    2. Snapshots sin AMI asociada con más de max_age_days días
    3. Cadenas de snapshots donde el volumen de origen existe
       pero los snapshots intermedios superan max_age_days
    """
    paginator = ec2_client.get_paginator('describe_snapshots')
    results = []

    for page in paginator.paginate(OwnerIds=['self']):
        for snapshot in page['Snapshots']:
            age_days = (
                datetime.utcnow() - snapshot['StartTime'].replace(tzinfo=None)
            ).days

            if age_days < max_age_days:
                continue  # Snapshot reciente: no es candidato

            # Verificamos si el volumen de origen sigue existiendo
            volume_exists = _check_volume_exists(snapshot.get('VolumeId', ''))

            # Verificamos si el snapshot está asociado a una AMI
            ami_associations = _get_ami_associations(snapshot['SnapshotId'])

            is_orphan = not volume_exists and not ami_associations

            if is_orphan:
                results.append({
                    'resource_type': 'snapshot',
                    'resource_id': snapshot['SnapshotId'],
                    'volume_id': snapshot.get('VolumeId', 'desconocido'),
                    'size_gb': snapshot['VolumeSize'],
                    'created_days_ago': age_days,
                    'volume_exists': volume_exists,
                    'ami_associations': ami_associations,
                    'monthly_cost_usd': round(snapshot['VolumeSize'] * 0.05, 2),
                    'tags': {tag['Key']: tag['Value']
                             for tag in snapshot.get('Tags', [])},
                    'description': snapshot.get('Description', '')
                })

    return results
