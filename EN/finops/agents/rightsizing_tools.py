# Source: The FinOps Engineer and the Machine -- Chapter 14
# Pattern: Rightsizing agent tools (EC2, RDS metrics)

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
    Gets EC2 instances with rightsizing recommendations from Compute Optimizer.
    Filters only recommendations with savings >$50/month to avoid noise.
    """
    response = optimizer_client.get_ec2_instance_recommendations(
        filters=[
            {
                'name': 'Finding',
                'values': ['OVER_PROVISIONED']  # Only oversized ones
            }
        ]
    )

    candidates = []
    for rec in response.get('instanceRecommendations', []):
        # Take the first rightsizing option (the one AWS recommends)
        if not rec.get('recommendationOptions'):
            continue

        best_option = rec['recommendationOptions'][0]
        monthly_savings = float(
            best_option.get('estimatedMonthlySavings', {}).get('value', 0)
        )

        if monthly_savings < 50:  # Minimum savings threshold
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
    Gets detailed CloudWatch metrics for a specific instance.
    Includes p50, p90, and p99 percentiles to detect real spikes.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=28)  # 4 weeks of history

    metrics_to_fetch = ['CPUUtilization', 'NetworkIn', 'NetworkOut']
    result = {'instance_id': instance_id, 'metrics': {}}

    for metric_name in metrics_to_fetch:
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # Hourly granularity
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

    # Also get instance tags (owner, environment, etc.)
    tags_response = ec2_client.describe_tags(
        Filters=[{'Name': 'resource-id', 'Values': [instance_id]}]
    )
    result['tags'] = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}

    return result


def _extract_key_metrics(utilization_metrics: list) -> dict:
    """Extracts key utilization metrics from Compute Optimizer response."""
    key_metrics = {}
    for metric in utilization_metrics:
        if metric['name'] in ['CPU_UTILIZATION', 'MEMORY_UTILIZATION']:
            key_metrics[metric['name']] = {
                'value': round(float(metric.get('value', 0)), 1),
                'statistic': metric.get('statistic', 'AVERAGE')
            }
    return key_metrics
