# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: AWS Cost and Usage Reports setup

import boto3

cur_client = boto3.client("cur", region_name="us-east-1")

# List configured reports
reports = cur_client.describe_report_definitions()
for report in reports["ReportDefinitions"]:
    print(f"Report: {report['ReportName']}")
    print(f"  Bucket: {report['S3Bucket']}")
    print(f"  Format: {report['Format']}")
    print(f"  Granularity: {report['TimeUnit']}")
