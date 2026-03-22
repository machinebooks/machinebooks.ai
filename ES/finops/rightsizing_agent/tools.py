# Extraído de: LibroFinOps/cap-14-rightsizing-ia.md
# rightsizing_agent/tools.py
import boto3
import json
from datetime import datetime, timedelta
from typing import Any

ec2_client = boto3.client('ec2', region_name='us-east-1')
cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
optimizer_client = boto3.client('compute-optimizer', region_name='us-east-1')


def get_ec2_rightsizing_candidates() -> dict:
    """
    Obtiene instancias EC2 con recomendaciones de rightsizing de Compute Optimizer.
    Filtra solo las recomendaciones con ahorro >$50/mes para evitar ruido.
    """
    response = optimizer_client.get_ec2_instance_recommendations(
        filters=[
            {
                'name': 'Finding',
                'values': ['OVER_PROVISIONED']  # Solo las sobredimensionadas
            }
        ]
    )

    candidates = []
    for rec in response.get('instanceRecommendations', []):
        # Tomamos la primera opción de rightsizing (la recomendada por AWS)
        if not rec.get('recommendationOptions'):
            continue

        best_option = rec['recommendationOptions'][0]
        monthly_savings = float(
            best_option.get('estimatedMonthlySavings', {}).get('value', 0)
        )

        if monthly_savings < 50:  # Umbral mínimo de ahorro
            continue

        candidates.append({
            'instance_id': rec['instanceArn'].split('/')[-1],
            'instance_arn': rec['instanceArn'],
            'current_type': rec['currentInstanceType'],
            'recommended_type': best_option['instanceType'],
            'monthly_savings_usd': round(monthly_savings, 2),
            'current_monthly_cost_usd': round(
                float(rec.get('currentOnDemandPrice', 0)) * 730, 2
            ),
            'finding': rec.get('finding', 'OVER_PROVISIONED'),
            'utilization_metrics': _extract_key_metrics(
                rec.get('utilizationMetrics', [])
            )
        })

    return {'candidates': candidates, 'total': len(candidates)}


def get_instance_utilization_detail(instance_id: str) -> dict:
    """
    Obtiene métricas detalladas de CloudWatch para una instancia específica.
    Incluye percentiles p50, p90 y p99 para detectar picos reales.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=28)  # 4 semanas de historia

    metrics_to_fetch = ['CPUUtilization', 'NetworkIn', 'NetworkOut']
    result = {'instance_id': instance_id, 'metrics': {}}

    for metric_name in metrics_to_fetch:
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # Granularidad hourly
            Statistics=['Average', 'Maximum']
        )

        if response['Datapoints']:
            values = [d['Average'] for d in response['Datapoints']]
            max_values = [d['Maximum'] for d in response['Datapoints']]
            result['metrics'][metric_name] = {
                'avg': round(sum(values) / len(values), 1),
                'max': round(max(max_values), 1),
                'p90': round(sorted(values)[int(len(values) * 0.9)], 1)
            }

    # Obtenemos también las etiquetas de la instancia (propietario, entorno, etc.)
    tags_response = ec2_client.describe_tags(
        Filters=[{'Name': 'resource-id', 'Values': [instance_id]}]
    )
    result['tags'] = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}

    return result


def _extract_key_metrics(utilization_metrics: list) -> dict:
    """Extrae las métricas clave de utilización de la respuesta de Compute Optimizer."""
    key_metrics = {}
    for metric in utilization_metrics:
        if metric['name'] in ['CPU_UTILIZATION', 'MEMORY_UTILIZATION']:
            key_metrics[metric['name']] = {
                'value': round(float(metric.get('value', 0)), 1),
                'statistic': metric.get('statistic', 'AVERAGE')
            }
    return key_metrics
