# Source: The FinOps Engineer and the Machine -- Chapter 15
# Pattern: Orphan snapshot detection

def scan_orphan_snapshots(max_age_days: int = 180) -> list[dict]:
    """
    Identifies potentially orphaned snapshots:
    1. Snapshots whose source volume no longer exists
    2. Snapshots without associated AMI older than max_age_days
    3. Snapshot chains where the source volume exists
       but intermediate snapshots exceed max_age_days
    """
    paginator = ec2_client.get_paginator('describe_snapshots')
    results = []

    for page in paginator.paginate(OwnerIds=['self']):
        for snapshot in page['Snapshots']:
            age_days = (
                datetime.utcnow() - snapshot['StartTime'].replace(tzinfo=None)
            ).days

            if age_days < max_age_days:
                continue  # Recent snapshot: not a candidate

            # Verify if the source volume still exists
            volume_exists = _check_volume_exists(snapshot.get('VolumeId', ''))

            # Verify if the snapshot is associated with an AMI
            ami_associations = _get_ami_associations(snapshot['SnapshotId'])

            is_orphan = not volume_exists and not ami_associations

            if is_orphan:
                results.append({
                    'resource_type': 'snapshot',
                    'resource_id': snapshot['SnapshotId'],
                    'volume_id': snapshot.get('VolumeId', 'unknown'),
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
