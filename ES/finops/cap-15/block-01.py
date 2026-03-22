# Extraído de: LibroFinOps/cap-15-waste-automatico.md
def scan_empty_load_balancers() -> list[dict]:
    """
    Lista los Application Load Balancers sin targets registrados.
    Un ALB vacío cuesta ~$16-22/mes (LCU + hourly rate).
    """
    paginator = elb_client.get_paginator('describe_load_balancers')
    results = []

    for page in paginator.paginate():
        for lb in page['LoadBalancers']:
            # Comprobamos si tiene target groups con targets registrados
            tg_response = elb_client.describe_target_groups(
                LoadBalancerArn=lb['LoadBalancerArn']
            )

            has_active_targets = False
            for tg in tg_response['TargetGroups']:
                health_response = elb_client.describe_target_health(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                if health_response['TargetHealthDescriptions']:
                    has_active_targets = True
                    break

            if not has_active_targets:
                age_days = (
                    datetime.utcnow() - lb['CreatedTime'].replace(tzinfo=None)
                ).days

                results.append({
                    'resource_type': 'load_balancer',
                    'resource_id': lb['LoadBalancerArn'].split('/')[-2],
                    'load_balancer_name': lb['LoadBalancerName'],
                    'type': lb['Type'],
                    'created_days_ago': age_days,
                    'monthly_cost_usd': 18.0,  # Estimación conservadora
                    'tags': _get_lb_tags(lb['LoadBalancerArn'])
                })

    return results


def _get_volume_last_access(volume_id: str) -> int | None:
    """
    Calcula cuántos días hace desde el último acceso de I/O al volumen.
    Usa métricas de CloudWatch VolumeReadOps y VolumeWriteOps.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=90)  # Buscamos en los últimos 90 días

    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EBS',
        MetricName='VolumeReadOps',
        Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,  # Granularidad diaria
        Statistics=['Sum']
    )

    if not response['Datapoints']:
        return 90  # Sin datos en 90 días: asumimos >90 días sin acceso

    # Encontramos el último datapoint con actividad > 0
    active_days = [
        d for d in response['Datapoints']
        if d['Sum'] > 0
    ]

    if not active_days:
        return 90

    last_active = max(active_days, key=lambda d: d['Timestamp'])
    days_ago = (end_time - last_active['Timestamp'].replace(tzinfo=None)).days
    return days_ago
