# Source: The DevSecOps and the Machine -- Chapter 6
# Pattern: Semantic secret detection with Claude

import anthropic
import json
from dataclasses import dataclass

@dataclass
class SecretFinding:
    file: str
    line: int
    pattern: str
    confidence: str  # "high", "medium", "low"
    reason: str
    recommendation: str

def analyze_diff_for_secrets(diff_content: str) -> list[SecretFinding]:
    """Analyze a Git diff looking for non-obvious secrets with Claude."""
    client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

    system_prompt = """You are a security analyst specializing in detecting
leaked secrets in source code. Your task is to analyze Git diffs
and detect secrets that regex-based tools would NOT detect.

Look specifically for:
1. Passwords as string literals without an identifiable prefix
2. Tokens in non-standard proprietary formats
3. Encryption keys encoded in base64 or hexadecimal
4. Credentials embedded in URLs not following standard connection patterns
5. High-entropy values assigned to variables whose name suggests a secret
6. Comments containing "temporary" test credentials

Do NOT report:
- Git commit hashes
- Non-sensitive identification UUIDs
- Values that are clearly placeholders (<YOUR_API_KEY>, xxxx, example)
- File checksums (SHA-256 of dependencies)

For each finding, respond in JSON with: file, line, pattern,
confidence (high/medium/low), reason, recommendation."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Analyze this diff for secrets:\n\n{diff_content}"
        }]
    )

    # Parse the model's JSON response
    findings = json.loads(message.content[0].text)
    return [SecretFinding(**f) for f in findings]