# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/prompt_manager.py
from datetime import datetime

class PromptManager:
    """
    Gestiona los 128 prompts versionados de la plataforma.
    Los prompts se cargan desde base de datos con caché en Redis.
    """

    CACHE_TTL = 300  # 5 minutos: balance entre frescura y rendimiento

    def get_prompt(self, prompt_key: str, version: str = "active") -> str:
        """
        Carga el prompt activo para una clave dada.
        Permite A/B testing cuando version="experiment".
        """
        cache_key = f"prompt:{prompt_key}:{version}"

        # Intentar caché Redis primero
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        # Cargar desde base de datos
        template = self._db.query(LLMPromptTemplate).filter(
            LLMPromptTemplate.key == prompt_key,
            LLMPromptTemplate.status == version
        ).first()

        if not template:
            raise PromptNotFoundError(f"Prompt no encontrado: {prompt_key}")

        # Guardar en caché
        self._cache.setex(cache_key, self.CACHE_TTL, template.content)

        return template.content

    def publish_version(
        self,
        prompt_key: str,
        content: str,
        author_id: str,
        notes: str
    ) -> LLMPromptTemplate:
        """
        Publica una nueva versión de un prompt.
        Desactiva la versión anterior automáticamente.
        """
        # Desactivar versión activa anterior
        self._db.query(LLMPromptTemplate).filter(
            LLMPromptTemplate.key == prompt_key,
            LLMPromptTemplate.status == "active"
        ).update({"status": "archived", "archived_at": datetime.utcnow()})

        # Crear nueva versión activa
        new_version = LLMPromptTemplate(
            key=prompt_key,
            content=content,
            status="active",
            version=self._next_version(prompt_key),
            author_id=author_id,
            notes=notes,
            content_hash=hashlib.sha256(content.encode()).hexdigest()
        )
        self._db.add(new_version)
        self._db.commit()

        # Invalidar caché
        self._cache.delete(f"prompt:{prompt_key}:active")

        return new_version
