# Extraído de: LibroPQC/cap-11-analisis-semantico.md
def detect_ai_providers() -> Dict[str, Dict]:
    """Detectar qué proveedores de IA están disponibles"""
    results = {}

    # Proveedores locales: sondear con timeout corto
    try:
        ollama = OllamaProvider({'base_url': os.environ.get(
            'OLLAMA_HOST', 'http://host.docker.internal:11434'
        )})
        status = ollama.test_connection()
        results['ollama'] = {
            'available': status.get('status') == 'success',
            'models': status.get('available_models', [])
        }
    except Exception:  # Capturar solo excepciones, nunca bare except
        results['ollama'] = {'available': False}

    # Proveedores cloud: verificar variables de entorno
    results['anthropic'] = {
        'available': bool(os.getenv('ANTHROPIC_API_KEY')),
        'configured': bool(os.getenv('ANTHROPIC_API_KEY'))
    }

    results['openai'] = {
        'available': bool(os.getenv('OPENAI_API_KEY')),
        'configured': bool(os.getenv('OPENAI_API_KEY'))
    }

    # Azure OpenAI: requiere endpoint + key + deployment
    azure_configured = bool(
        os.getenv('AZURE_OPENAI_ENDPOINT') and
        os.getenv('AZURE_OPENAI_API_KEY') and
        os.getenv('AZURE_OPENAI_DEPLOYMENT')
    )
    results['azure_openai'] = {
        'available': azure_configured,
        'configured': azure_configured
    }

    return results
