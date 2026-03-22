# Source: The FinOps Engineer and the Machine -- Chapter 15
# Pattern: Waste cleanup task with safety guards

# tasks/waste_cleanup.py
from celery import Celery
import boto3
import json

celery_app = Celery('waste_cleanup')
ec2_client = boto3.client('ec2', region_name='us-east-1')
elb_client = boto3.client('elbv2', region_name='us-east-1')


@celery_app.task(name='execute_waste_cleanup')
def execute_waste_cleanup(
    resource_ids: list[str],
    resource_types: dict[str, str],  # {resource_id: resource_type}
    dry_run: bool = True  # Always dry_run=True by default
):
    """
    Executes the deletion of approved orphaned resources.
    dry_run=True is the default behavior: never delete without confirmation.
    """
    results = []

    for resource_id in resource_ids:
        resource_type = resource_types.get(resource_id)

        try:
            if resource_type == 'ebs_volume':
                result = _delete_ebs_volume(resource_id, dry_run)
            elif resource_type == 'elastic_ip':
                result = _release_elastic_ip(resource_id, dry_run)
            elif resource_type == 'load_balancer':
                result = _delete_load_balancer(resource_id, dry_run)
            else:
                result = {'status': 'skipped', 'reason': 'Unknown resource type'}

            results.append({'resource_id': resource_id, **result})

        except Exception as e:
            # Any deletion error should not stop the rest
            results.append({
                'resource_id': resource_id,
                'status': 'error',
                'error': str(e)
            })

    return {
        'dry_run': dry_run,
        'total_processed': len(results),
        'results': results
    }
