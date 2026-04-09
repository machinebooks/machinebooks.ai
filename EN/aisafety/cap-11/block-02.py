# Extracted from: LibroAISafety/ch-11-red-teaming.md
# Generating aggregated engagement metrics
# For the executive report, not technical

def generate_metrics(attempts: list[RedTeamAttempt]) -> dict:
    """Calculates aggregated metrics for the report."""
    total = len(attempts)
    if total == 0:
        return {"error": "No attempts recorded"}

    successes = sum(1 for i in attempts
                    if i.classification == ResultClassification.SUCCESS)
    partials = sum(1 for i in attempts
                   if i.classification == ResultClassification.PARTIAL)

    # Breakdown by category
    by_category = {}
    for cat in AttackCategory:
        cat_attempts = [i for i in attempts if i.category == cat]
        cat_successes = [i for i in cat_attempts
                         if i.classification == ResultClassification.SUCCESS]
        if cat_attempts:
            by_category[cat.value] = {
                "attempts": len(cat_attempts),
                "successes": len(cat_successes),
                "rate": round(len(cat_successes) / len(cat_attempts), 3),
            }

    return {
        "total_attempts": total,
        "successes": successes,
        "partials": partials,
        "global_success_rate": round(successes / total, 3),
        "by_category": by_category,
    }
