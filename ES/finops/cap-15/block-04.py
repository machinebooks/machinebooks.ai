# Extraído de: LibroFinOps/cap-15-waste-automatico.md
def _delete_ebs_volume(volume_id: str, dry_run: bool) -> dict:
    """Elimina un volumen EBS. Verifica que sigue sin attachment antes de borrar."""
    # Re-verificamos el estado antes de borrar (puede haber cambiado desde el escaneo)
    response = ec2_client.describe_volumes(VolumeIds=[volume_id])
    volume = response['Volumes'][0]

    if volume['State'] != 'available':
        return {
            'status': 'skipped',
            'reason': f"Volumen ya no está disponible: estado actual {volume['State']}"
        }

    if dry_run:
        return {
            'status': 'dry_run_ok',
            'message': f"Habría eliminado volumen {volume_id} ({volume['Size']} GB)"
        }

    ec2_client.delete_volume(VolumeId=volume_id)
    return {'status': 'deleted', 'size_gb': volume['Size']}


def _release_elastic_ip(allocation_id: str, dry_run: bool) -> dict:
    """Libera una Elastic IP. Verifica que sigue sin asociación antes de liberar."""
    response = ec2_client.describe_addresses(AllocationIds=[allocation_id])
    address = response['Addresses'][0]

    if 'AssociationId' in address:
        return {
            'status': 'skipped',
            'reason': 'EIP ya está asociada a una instancia'
        }

    if dry_run:
        return {
            'status': 'dry_run_ok',
            'message': f"Habría liberado EIP {address['PublicIp']}"
        }

    ec2_client.release_address(AllocationId=allocation_id)
    return {'status': 'released', 'public_ip': address['PublicIp']}
