"""
PQC-Day and the Machine — Chapter 11
Pattern: AICodeAnalyzer — multi-provider AI code analysis with Claude API

This is a didactic example from the book, not production code.
See chapter 11 for full context and explanation.
"""

import json
import os
import re
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    CUSTOM = "custom"


@dataclass
class AIAnalysisResult:
    """Structured result from AI analysis."""
    provider: str
    model: str
    findings: List[Dict]
    summary: str
    risk_score: float
    recommendations: List[str]
    quantum_vulnerable_items: List[Dict]
    pqc_migration_plan: List[Dict]
    raw_response: Optional[str] = None
    tokens_used: Optional[int] = None
    analysis_time_ms: Optional[int] = None


class BaseAIProvider(ABC):
    """Base class for all AI providers."""

    def __init__(self, config: Dict, analysis_type: str = 'pqc'):
        self.config = config
        self.model = config.get('model')
        self.timeout = config.get('timeout', 120)
        self.analysis_type = analysis_type

    @abstractmethod
    def analyze_code(self, code: str, filename: str,
                     context: Dict = None) -> Dict:
        pass

    @abstractmethod
    def test_connection(self) -> Dict:
        pass

    def _build_pqc_prompt(self, code: str, filename: str,
                          language: str = None) -> str:
        """Prompt specialized in post-quantum cryptography."""
        return f"""You are an expert in post-quantum cryptography (PQC).
Analyze the following code for cryptographic vulnerabilities
that will be exploitable by quantum computers.

**FILE:** {filename}
**LANGUAGE:** {language or 'auto-detect'}

**CODE:**
```
{code}
```

**INSTRUCTIONS:**
1. Identify ALL cryptographic algorithms used
2. Classify each one as:
   - CRITICAL: RSA, DSA, ECDSA, ECDH, DH (vulnerable to Shor)
   - HIGH: SHA-1, MD5, DES, 3DES (weak or broken)
   - MEDIUM: AES-128 (reduced security with Grover)
   - LOW: AES-256, SHA-384/512 (post-quantum secure)
3. Provide PQC migration recommendations

**RESPOND IN VALID JSON:**
{{
    "findings": [...],
    "summary": "executive summary",
    "risk_score": 0-100,
    "quantum_vulnerable": [...],
    "pqc_migration_plan": [...],
    "recommendations": [...]
}}

Respond ONLY with the JSON, no additional text."""

    def _build_owasp_prompt(self, code: str, filename: str,
                            language: str = None) -> str:
        """Prompt specialized in OWASP Top 10 analysis."""
        return f"""You are an application security expert specializing in
OWASP Top 10 vulnerabilities.
Analyze the following code for security vulnerabilities.

**FILE:** {filename}
**LANGUAGE:** {language or 'auto-detect'}

**CODE:**
```
{code}
```

**INSTRUCTIONS:**
Identify vulnerabilities from these OWASP Top 10 categories:

1. **A01:2021 - Broken Access Control**
2. **A02:2021 - Cryptographic Failures**
3. **A03:2021 - Injection**
4. **A04:2021 - Insecure Design**
5. **A05:2021 - Security Misconfiguration**
6. **A06:2021 - Vulnerable Components**
7. **A07:2021 - Auth Failures**
8. **A08:2021 - Integrity Failures**
9. **A09:2021 - Logging Failures**
10. **A10:2021 - SSRF**

**RESPOND IN VALID JSON:**
{{
    "findings": [
        {{
            "type": "owasp_vulnerability",
            "owasp_category": "A01|A02|...|A10",
            "vulnerability_name": "name",
            "severity": "critical|high|medium|low",
            "line_number": null,
            "description": "detailed description",
            "impact": "potential impact",
            "recommendation": "how to fix it",
            "cwe_id": "CWE-XXX if applicable"
        }}
    ],
    "summary": "executive summary of the OWASP analysis",
    "risk_score": 0-100
}}"""

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response to JSON with graceful degradation."""
        # Attempt 1: direct parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Attempt 2: extract JSON block from text
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Attempt 3: return empty structure (do not silence the failure)
        logger.warning("Could not parse AI response as JSON")
        return {
            'findings': [],
            'summary': response_text[:500],
            'risk_score': 0,
            'quantum_vulnerable': [],
            'pqc_migration_plan': [],
            'recommendations': ['Could not parse AI response']
        }


class AnthropicProvider(BaseAIProvider):
    """Anthropic provider (Claude)."""

    def __init__(self, config: Dict, analysis_type: str = 'pqc'):
        super().__init__(config, analysis_type)
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.model = config.get('model', 'claude-sonnet-4-6')

    def analyze_code(self, code: str, filename: str,
                     context: Dict = None) -> Dict:
        """Analyze code using Claude API."""
        try:
            import anthropic
        except ImportError:
            return {'error': 'anthropic package not installed'}

        language = context.get('language') if context else None

        if self.analysis_type == 'owasp':
            prompt = self._build_owasp_prompt(code, filename, language)
            system_msg = ('You are an application security expert '
                          'specializing in OWASP Top 10 vulnerabilities.')
        else:
            prompt = self._build_pqc_prompt(code, filename, language)
            system_msg = ('You are a cryptography security expert '
                          'specializing in post-quantum cryptography.')

        client = anthropic.Anthropic(api_key=self.api_key)

        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_msg,
            messages=[{'role': 'user', 'content': prompt}]
        )

        content = response.content[0].text
        result = self._parse_ai_response(content)
        result['tokens_used'] = (
            response.usage.input_tokens + response.usage.output_tokens
        )
        return result

    def test_connection(self) -> Dict:
        """Test connection to Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{'role': 'user', 'content': 'ping'}]
            )
            return {'status': 'success', 'model': self.model}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class AICodeAnalyzer:
    """AI code analyzer — unified multi-provider interface."""

    PROVIDERS = {
        'anthropic': AnthropicProvider,
        # Additional providers: OpenAIProvider, OllamaProvider, etc.
    }

    def __init__(self, provider: str = 'anthropic',
                 analysis_type: str = 'pqc', **config):
        self.provider_name = provider
        self.analysis_type = analysis_type

        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available: {list(self.PROVIDERS.keys())}"
            )

        self.provider = self.PROVIDERS[provider](config, analysis_type)

    def analyze_file(self, code: str, filename: str,
                     context: Dict = None) -> AIAnalysisResult:
        """Analyze a file — measures time and encapsulates errors."""
        start_time = time.time()
        result = self.provider.analyze_code(code, filename, context)
        elapsed_ms = int((time.time() - start_time) * 1000)

        if 'error' in result:
            return AIAnalysisResult(
                provider=self.provider_name,
                model=self.provider.model,
                findings=[], summary=f"Error: {result['error']}",
                risk_score=0, recommendations=[],
                quantum_vulnerable_items=[], pqc_migration_plan=[],
                analysis_time_ms=elapsed_ms
            )

        return AIAnalysisResult(
            provider=self.provider_name,
            model=self.provider.model,
            findings=result.get('findings', []),
            summary=result.get('summary', ''),
            risk_score=result.get('risk_score', 0),
            recommendations=result.get('recommendations', []),
            quantum_vulnerable_items=result.get('quantum_vulnerable', []),
            pqc_migration_plan=result.get('pqc_migration_plan', []),
            tokens_used=result.get('tokens_used'),
            analysis_time_ms=elapsed_ms
        )


def detect_ai_providers() -> Dict[str, Dict]:
    """Detect which AI providers are available."""
    results = {}

    results['anthropic'] = {
        'available': bool(os.getenv('ANTHROPIC_API_KEY')),
        'configured': bool(os.getenv('ANTHROPIC_API_KEY'))
    }
    results['openai'] = {
        'available': bool(os.getenv('OPENAI_API_KEY')),
        'configured': bool(os.getenv('OPENAI_API_KEY'))
    }

    return results


# --- Main ---
if __name__ == '__main__':
    sample_code = '''
from Crypto.PublicKey import RSA
import hashlib

# Generate RSA key pair
key = RSA.generate(2048)

# Hash with MD5 (broken)
digest = hashlib.md5(data).hexdigest()

# Hash with SHA-256 (acceptable post-quantum)
secure_digest = hashlib.sha256(data).hexdigest()
'''

    providers = detect_ai_providers()
    print("Available providers:", {k: v['available'] for k, v in providers.items()})

    if providers.get('anthropic', {}).get('available'):
        analyzer = AICodeAnalyzer(
            provider='anthropic',
            analysis_type='pqc',
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            model='claude-sonnet-4-6'
        )
        result = analyzer.analyze_file(sample_code, 'crypto_example.py')
        print(f"\nProvider: {result.provider}")
        print(f"Model: {result.model}")
        print(f"Risk score: {result.risk_score}")
        print(f"Findings: {len(result.findings)}")
        print(f"Tokens used: {result.tokens_used}")
        print(f"Time: {result.analysis_time_ms}ms")
        print(f"\nSummary: {result.summary}")
    else:
        print("\nSet ANTHROPIC_API_KEY to run the analysis.")
