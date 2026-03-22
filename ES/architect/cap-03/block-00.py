# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
class AnthropicOpenAIAdapter:
    """Adapta el cliente nativo de Anthropic a la interfaz OpenAI
    para unificar el patrón de tool calling en toda la aplicación."""

    def __init__(self, anthropic_client):
        self._anthropic = anthropic_client
        self.chat = _SyncChatNS(anthropic_client)
        self.messages = anthropic_client.messages

    def __getattr__(self, name):
        # Cualquier atributo no definido se delega al cliente nativo
        return getattr(self._anthropic, name)
