# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
import boto3

cur_client = boto3.client("cur", region_name="us-east-1")

# Listar reportes configurados
reports = cur_client.describe_report_definitions()
for report in reports["ReportDefinitions"]:
    print(f"Reporte: {report['ReportName']}")
    print(f"  Bucket: {report['S3Bucket']}")
    print(f"  Formato: {report['Format']}")
    print(f"  Granularidad: {report['TimeUnit']}")
