# Extraído de: LibroPQC/cap-11-analisis-semantico.md
class AICodeAnalyzer:
    """Analizador de código con IA — interfaz unificada multi-proveedor"""

    PROVIDERS = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'azure_openai': AzureOpenAIProvider,
        'ollama': OllamaProvider,
        'lmstudio': LMStudioProvider,
        'custom': CustomOpenAIProvider,
    }

    def __init__(self, provider: str = 'ollama',
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
        """Analizar un fichero — mide tiempo y encapsula errores"""
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
