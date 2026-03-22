# Source: The FinOps Engineer and the Machine -- Chapter 5
# Pattern: Apply approved tag corrections to AWS resources

# tasks/apply_tag_corrections.py
import boto3

def apply_approved_tag_corrections(proposal_ids: list[str]) -> dict:
    """
    Applies tag corrections approved by the FinOps team.
    Only processes proposals in 'approved' status.
    Records the result of each application.
    """
    ec2 = boto3.client("ec2", region_name="eu-west-1")
    results = {"applied": [], "failed": []}

    for proposal_id in proposal_ids:
        # Load the approved proposal from database
        proposal = load_proposal(proposal_id)
        if proposal["status"] != "approved":
            continue

        try:
            if proposal["resource_type"] == "EC2":
                ec2.create_tags(
                    Resources=[proposal["resource_id"]],
                    Tags=[
                        {"Key": k, "Value": v}
                        for k, v in proposal["proposed_tags"].items()
                    ],
                )
                update_proposal_status(proposal_id, "applied")
                results["applied"].append(proposal_id)
        except Exception as exc:
            update_proposal_status(proposal_id, "failed", error=str(exc))
            results["failed"].append({"id": proposal_id, "error": str(exc)})

    return results
