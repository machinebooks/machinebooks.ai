# Extraído de: LibroFinOps/cap-14-rightsizing-ia.md
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
    Ejecuta el cambio de tipo de instancia.
    Siempre verifica que la instancia esté parada antes de modificarla.
    dry_run=True para verificar permisos sin ejecutar el cambio.
    """
    if dry_run:
        # Verificamos permisos sin ejecutar nada
        try:
            ec2_client.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type},
                DryRun=True  # AWS valida permisos sin aplicar
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DryRunOperation':
                return {'status': 'dry_run_ok', 'message': 'Permisos verificados'}
            raise

    # Verificamos el estado actual de la instancia
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    current_state = instance['State']['Name']

    if current_state == 'running':
        # Detenemos la instancia antes de modificarla
        ec2_client.stop_instances(InstanceIds=[instance_id])
        _wait_for_instance_state(instance_id, 'stopped')

    # Modificamos el tipo de instancia
    ec2_client.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={'Value': new_instance_type}
    )

    # Arrancamos de nuevo si estaba running
    if current_state == 'running':
        ec2_client.start_instances(InstanceIds=[instance_id])
        _wait_for_instance_state(instance_id, 'running')

    return {
        'status': 'completed',
        'instance_id': instance_id,
        'new_type': new_instance_type
    }
