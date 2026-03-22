# Source: The FinOps Engineer and the Machine -- Chapter 26
# Pattern: EC2 rightsizing scanner

def _scan_ec2(self, min_cpu_threshold: float) -> dict:
    """EC2 scanning with CloudWatch metrics."""
    instancias = []
    paginator = self.ec2.get_paginator("describe_instances")

    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    ):
        for reservation in page["Reservations"]:
            for inst in reservation["Instances"]:
                # Average CPU over the last 30 days (daily data points)
                cpu_stats = self.cloudwatch.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="CPUUtilization",
                    Dimensions=[{
                        "Name": "InstanceId",
                        "Value": inst["InstanceId"]
                    }],
                    StartTime=datetime.utcnow() - timedelta(days=30),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=["Average"],
                )

                cpu_valores = [p["Average"] for p in cpu_stats["Datapoints"]]
                cpu_media = (
                    sum(cpu_valores) / len(cpu_valores) if cpu_valores else 0
                )

                instancias.append({
                    "instance_id": inst["InstanceId"],
                    "instance_type": inst["InstanceType"],
                    "cpu_media_pct": round(cpu_media, 2),
                    "infrautilizada": cpu_media < min_cpu_threshold,
                    "coste_mensual_est_usd": self._estimar_coste(
                        inst["InstanceType"]
                    ),
                    "tags": {
                        t["Key"]: t["Value"]
                        for t in inst.get("Tags", [])
                    },
                })

    return {
        "instancias": instancias,
        "total": len(instancias),
        "infrautilizadas": sum(
            1 for i in instancias if i["infrautilizada"]
        ),
    }
