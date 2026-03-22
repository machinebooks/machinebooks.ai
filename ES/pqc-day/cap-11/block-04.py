# Extraído de: LibroPQC/cap-11-analisis-semantico.md
class AnthropicProvider(BaseAIProvider):
    """Proveedor Anthropic (Claude)"""

    def __init__(self, config: Dict, analysis_type: str = 'pqc'):
        super().__init__(config, analysis_type)
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.base_url = 'https://api.anthropic.com/v1'
        self.model = config.get('model', 'claude-sonnet-4-6')

    def analyze_code(self, code: str, filename: str,
                     context: Dict = None) -> Dict:
        language = context.get('language') if context else None

        # Seleccionar prompt según tipo de análisis
        if self.analysis_type == 'owasp':
            prompt = self._build_owasp_prompt(code, filename, language)
        else:
            prompt = self._build_pqc_prompt(code, filename, language)

        response = requests.post(
            f"{self.base_url}/messages",
            headers={
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': self.model,
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            content = data['content'][0]['text']
            result = self._parse_ai_response(content)
            # Registrar tokens para gobernanza (cap 14)
            result['tokens_used'] = (
                data.get('usage', {}).get('input_tokens', 0) +
                data.get('usage', {}).get('output_tokens', 0)
            )
            return result
        else:
            logger.error(f"Anthropic API error: {response.text}")
            return {'error': f'API error: {response.status_code}'}
