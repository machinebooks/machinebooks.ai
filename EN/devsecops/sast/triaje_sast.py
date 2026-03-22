# Source: The DevSecOps and the Machine -- Chapter 4
# Pattern: Tiered SAST triage: Haiku filters, Sonnet analyzes

import json
import anthropic

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

TRIAGE_PROMPT = """You are a senior security engineer. Analyze
the following SAST finding and surrounding code.

Finding: {finding_id}
Reported severity: {severity}
Message: {message}
File: {file_path}
Line: {line}

Surrounding code (40 lines):

def tiered_triage(findings: list[dict]) -> list[dict]:
    """Two-phase triage pipeline: Haiku filters, Sonnet analyzes."""
    results = []

    # Phase 1: quick classification with Haiku
    for h in findings:
        context = read_surrounding_code(h["path"], h["start"]["line"])
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Classify this SAST finding as
"probable_true" or "probable_false". Only respond with JSON:
{{"classification": "...", "reason": "..."}}

Rule: {h["check_id"]}
Code:\n```\n{context}\n```""",
            }],
        )
        haiku_result = json.loads(response.content[0].text)
        h["triage_haiku"] = haiku_result

        # Only escalate to Sonnet if Haiku says probable true
        if haiku_result["classification"] == "probable_true":
            sonnet_result = triage_finding(h)
            h["triage_sonnet"] = sonnet_result
            results.append(h)

    return results