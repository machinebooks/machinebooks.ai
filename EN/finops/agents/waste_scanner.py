# Source: The FinOps Engineer and the Machine -- Chapter 15
# Pattern: Automated waste scanner (EBS, EIP, snapshots)

# waste_scanner/scanner.py
import boto3
from datetime import datetime, timedelta
from typing import Any

ec2_client = boto3.client('ec2', region_name='us-east-1')
cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
elb_client = boto3.client('elbv2', region_name='us-east-1')


def scan_unattached_ebs_volumes() -> list[dict]:
    """
    Lists all EBS volumes without an attached instance.
    Includes age, size, and estimated cost metadata.
    """
    response = ec2_client.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]  # available = no attachment
    )

    results = []
    for volume in response['Volumes']:
        # Estimated cost: $0.10/GB/month for gp2/gp3
        monthly_cost_usd = volume['Size'] * 0.10

        # Age since volume creation
        age_days = (datetime.utcnow() - volume['CreateTime'].replace(tzinfo=None)).days

        # Last access (I/O metrics in CloudWatch)
        last_access = _get_volume_last_access(volume['VolumeId'])

        results.append({
            'resource_type': 'ebs_volume',
            'resource_id': volume['VolumeId'],
            'size_gb': volume['Size'],
            'volume_type': volume['VolumeType'],
            'created_days_ago': age_days,
            'last_io_days_ago': last_access,
            'monthly_cost_usd': round(monthly_cost_usd, 2),
            'tags': {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])},
            'availability_zone': volume['AvailabilityZone']
        })

    return results


def scan_unused_elastic_ips() -> list[dict]:
    """
    Lists Elastic IPs not associated with any instance or network interface.
    """
    response = ec2_client.describe_addresses()
    results = []

    for address in response['Addresses']:
        # An EIP without AssociationId is free
        if 'AssociationId' in address:
            continue  # In use

        # Unused EIPs cost $0.005/hour = ~$3.65/month
        results.append({
            'resource_type': 'elastic_ip',
            'resource_id': address['AllocationId'],
            'public_ip': address['PublicIp'],
            'monthly_cost_usd': 3.65,
            'tags': {tag['Key']: tag['Value'] for tag in address.get('Tags', [])},
            'created_days_ago': None  # AWS does not expose EIP creation date
        })

    return results
