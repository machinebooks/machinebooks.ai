# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
def get_resource_creator(resource_id: str, region: str) -> dict | None:
    """
    Consulta CloudTrail para identificar quién creó un recurso EC2
    y en qué contexto (consola, CLI, SDK, pipeline de CI/CD).
    """
    import boto3
    from datetime import datetime, timedelta, timezone

    ct = boto3.client("cloudtrail", region_name=region)

    # Buscar el evento RunInstances en los últimos 90 días
    try:
        response = ct.lookup_events(
            LookupAttributes=[
                {"AttributeKey": "ResourceName", "AttributeValue": resource_id}
            ],
            StartTime=datetime.now(timezone.utc) - timedelta(days=90),
            EndTime=datetime.now(timezone.utc),
            MaxResults=5,
        )
    except Exception:
        return None

    for event in response.get("Events", []):
        if event.get("EventName") == "RunInstances":
            return {
                "creator_username": event.get("Username"),
                "creator_arn": event.get("UserIdentity", {}).get("arn"),
                "source_ip": event.get("SourceIPAddress"),
                "user_agent": event.get("UserAgent"),
                "event_time": event.get("EventTime").isoformat(),
            }

    return None
