# Source: The FinOps Engineer and the Machine -- Chapter 14
# Pattern: Safe execution of rightsizing actions

# tasks/rightsizing_executor.py
from celery import Celery
import boto3

celery_app = Celery('rightsizing_executor')
ec2_client = boto3.client('ec2', region_name='us-east-1')


@celery_app.task(name='execute_rightsizing')
def execute_rightsizing(
    instance_id: str, new_instance_type: str, dry_run: bool = False
):
    """
    Executes the instance type change.
    Always verifies the instance is stopped before modifying it.
    dry_run=True to verify permissions without executing the change.
    """
    if dry_run:
        # Verify permissions without executing anything
        try:
            ec2_client.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type},
                DryRun=True  # AWS validates permissions without applying
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DryRunOperation':
                return {'status': 'dry_run_ok', 'message': 'Permissions verified'}
            raise

    # Verify the current instance state
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    current_state = instance['State']['Name']

    if current_state == 'running':
        # Stop the instance before modifying it
        ec2_client.stop_instances(InstanceIds=[instance_id])
        _wait_for_instance_state(instance_id, 'stopped')

    # Modify the instance type
    ec2_client.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={'Value': new_instance_type}
    )

    # Start again if it was running
    if current_state == 'running':
        ec2_client.start_instances(InstanceIds=[instance_id])
        _wait_for_instance_state(instance_id, 'running')

    return {
        'status': 'completed',
        'instance_id': instance_id,
        'new_type': new_instance_type
    }
