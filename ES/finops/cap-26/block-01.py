# Extraído de: LibroFinOps/cap-26-caso-cloud.md
class CloudOptimizerAgent:
    """
    Agente que optimiza costes cloud usando Claude para análisis.

    Herramientas disponibles:
    - scan_ec2_instances: instancias con métricas de utilización
    - scan_ebs_volumes: volúmenes no adjuntos
    - get_monthly_cost_by_service: gasto por servicio AWS
    - execute_action_dry_run: simulación sin cambios reales
    """

    def __init__(self, aws_region: str = "eu-west-1"):
        self.client = anthropic.Anthropic()
        self.ec2 = boto3.client("ec2", region_name=aws_region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=aws_region)
        # Cost Explorer siempre en us-east-1
        self.ce = boto3.client("ce", region_name="us-east-1")
        self.region = aws_region
