# Extraído de: LibroFinOps/cap-15-waste-automatico.md
# waste_scanner/scanner.py
import boto3
from datetime import datetime, timedelta
from typing import Any

ec2_client = boto3.client('ec2', region_name='us-east-1')
cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
elb_client = boto3.client('elbv2', region_name='us-east-1')


def scan_unattached_ebs_volumes() -> list[dict]:
    """
    Lista todos los volúmenes EBS sin instancia adjunta.
    Incluye metadatos de antigüedad, tamaño y coste estimado.
    """
    response = ec2_client.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]  # available = sin attachment
    )

    results = []
    for volume in response['Volumes']:
        # Coste estimado: $0.10/GB/mes para gp2/gp3
        monthly_cost_usd = volume['Size'] * 0.10

        # Antigüedad desde la creación del volumen
        age_days = (datetime.utcnow() - volume['CreateTime'].replace(tzinfo=None)).days

        # Último acceso (métricas de I/O en CloudWatch)
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
    Lista las Elastic IPs no asociadas a ninguna instancia o interfaz de red.
    """
    response = ec2_client.describe_addresses()
    results = []

    for address in response['Addresses']:
        # Una EIP sin AssociationId está libre
        if 'AssociationId' in address:
            continue  # Está en uso

        # EIPs no usadas cuestan $0.005/hora = ~$3.65/mes
        results.append({
            'resource_type': 'elastic_ip',
            'resource_id': address['AllocationId'],
            'public_ip': address['PublicIp'],
            'monthly_cost_usd': 3.65,
            'tags': {tag['Key']: tag['Value'] for tag in address.get('Tags', [])},
            'created_days_ago': None  # AWS no expone la fecha de creación de EIPs
        })

    return results
