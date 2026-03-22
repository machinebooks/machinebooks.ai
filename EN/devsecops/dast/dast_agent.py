# Source: The DevSecOps and the Machine -- Chapter 12
# Pattern: Intelligent DAST with OpenAPI analysis and ZAP orchestration

import json
import yaml
from pathlib import Path

def parse_openapi_spec(spec_path: str) -> dict:
    """Analyzes an OpenAPI specification and extracts the attack surface."""
    with open(spec_path) as f:
        if spec_path.endswith(".yaml") or spec_path.endswith(".yml"):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)

    endpoints = []
    security_schemes = spec.get("components", {}).get("securitySchemes", {})

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                params = []
                # Path and query parameters
                for p in details.get("parameters", []):
                    params.append({
                        "name": p["name"],
                        "in": p["in"],
                        "type": p.get("schema", {}).get("type", "string"),
                        "required": p.get("required", False),
                    })
                # Request body
                request_body = details.get("requestBody", {})
                body_schema = {}
                if request_body:
                    content = request_body.get("content", {})
                    json_content = content.get("application/json", {})
                    body_schema = json_content.get("schema", {})

                # Endpoint security
                endpoint_security = details.get("security", spec.get("security", []))

                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "parameters": params,
                    "body_schema": body_schema,
                    "security": endpoint_security,
                    "tags": details.get("tags", []),
                    "summary": details.get("summary", ""),
                })

    return {
        "base_url": spec.get("servers", [{}])[0].get("url", ""),
        "endpoints": endpoints,
        "security_schemes": security_schemes,
        "total_endpoints": len(endpoints),
    }

import anthropic
import json

client = anthropic.Anthropic()

def generate_scan_plan(api_surface: dict) -> dict:
    """Generates a directed DAST scan plan with Claude."""
    prompt = f"""Analyze the following attack surface of a REST API
and generate a DAST scan plan. For each endpoint, indicate:
1. Vulnerabilities to test (from OWASP Top 10 and API Security Top 10)
2. Specific payloads for each parameter based on its type and context
3. Scan priority (high/medium/low) based on exposure and risk
4. Expected responses that would indicate a real vulnerability

Security rules:
- Do NOT generate destructive payloads (DROP TABLE, mass DELETE)
- Do NOT generate payloads for real data exfiltration
- Limit injections to detection, not full exploitation

Attack surface:
{json.dumps(api_surface, indent=2)}

Respond in JSON with the structure:
{{
  "scan_plan": [
    {{
      "endpoint": "/api/...",
      "method": "POST",
      "priority": "high",
      "tests": [
        {{
          "category": "sql_injection",
          "parameter": "email",
          "payloads": ["..."],
          "expected_vulnerable_response": "...",
          "expected_safe_response": "..."
        }}
      ]
    }}
  ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)

import subprocess
import json
import time
from pathlib import Path

def run_zap_scan(
    plan_path: str,
    target_url: str,
    results_dir: str = "/tmp/zap-results",
) -> dict:
    """Executes OWASP ZAP with the generated automation plan."""
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # Run ZAP in headless mode with the automation plan
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{plan_path}:/zap/plan.yaml:ro",
        "-v", f"{results_dir}:/zap/results",
        "--network", "host",
        "ghcr.io/zaproxy/zaproxy:stable",
        "zap.sh", "-cmd",
        "-autorun", "/zap/plan.yaml",
    ]

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - start_time

    # Read results
    report_path = Path(results_dir) / "zap-report.json"
    if report_path.exists():
        with open(report_path) as f:
            zap_results = json.load(f)
    else:
        zap_results = {"error": "No report generated", "stderr": result.stderr}

    return {
        "results": zap_results,
        "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 1),
        "stdout_summary": result.stdout[-500:] if result.stdout else "",
    }

def analyze_dast_results(
    zap_results: dict,
    api_surface: dict,
    scan_plan: dict,
) -> dict:
    """Analyzes ZAP results with Claude to filter false positives."""
    # Group alerts by endpoint and severity
    alerts = zap_results.get("site", [{}])[0].get("alerts", [])

    alert_summary = []
    for alert in alerts:
        alert_summary.append({
            "name": alert.get("name"),
            "risk": alert.get("riskdesc", "").split(" ")[0],
            "confidence": alert.get("confidence"),
            "url": alert.get("instances", [{}])[0].get("uri", ""),
            "param": alert.get("instances", [{}])[0].get("param", ""),
            "evidence": alert.get("instances", [{}])[0].get("evidence", "")[:200],
            "cwe_id": alert.get("cweid"),
            "description": alert.get("desc", "")[:300],
            "count": len(alert.get("instances", [])),
        })

    prompt = f"""You are an expert security analyst reviewing DAST results.

Application context:
- REST API with {api_surface['total_endpoints']} endpoints
- Authentication: JWT Bearer token
- Framework: FastAPI with SQLAlchemy (ORM with prepared statements)
- Database: PostgreSQL

ZAP alerts ({len(alert_summary)} alert types):
{json.dumps(alert_summary, indent=2)}

For each alert, classify as:
- REAL: confirmed vulnerability with clear evidence
- PROBABLE: requires manual verification but there are indications
- FALSE_POSITIVE: explain why it does not apply in this context

Analysis criteria:
1. A SQL injection alert in an app with ORM and prepared statements
   is probably a false positive unless evidence shows raw SQL
2. XSS on endpoints that return JSON (not HTML) is a false positive
3. SSRF requires the injected URL to resolve - verify evidence
4. Generic 400/422 errors are NOT evidence of vulnerability
5. Anomalous response times CAN indicate time-based injection

Respond in JSON:
{{
  "findings": [
    {{
      "alert_name": "...",
      "classification": "REAL|PROBABLE|FALSE_POSITIVE",
      "confidence": 0.0-1.0,
      "reasoning": "...",
      "recommended_action": "...",
      "cwe": "CWE-xxx"
    }}
  ],
  "summary": {{
    "total_alerts": N,
    "real": N,
    "probable": N,
    "false_positives": N,
    "risk_rating": "CRITICAL|HIGH|MEDIUM|LOW"
  }}
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)