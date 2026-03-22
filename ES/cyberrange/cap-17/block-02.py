# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/scenario_generator.py
from agents import Runner
from backend.services.ai.scenario_agent import scenario_agent, complex_scenario_agent
from backend.services.ai.scenario_validator import ScenarioValidator
from backend.models import ScenarioTemplate
from backend.database import get_db
import json

class ScenarioGeneratorService:
    """
    Servicio principal de generación de escenarios con IA.
    Orquesta el agente, la validación y el almacenamiento.
    """

    def __init__(self):
        self.validator = ScenarioValidator()

    async def generate_scenario(
        self,
        description: str,
        workzone_id: int,
        author_id: int,
        complexity: str = "standard"
    ) -> dict:
        """
        Genera un escenario completo desde una descripción en lenguaje natural.

        Args:
            description: Lo que el instructor quiere (lenguaje natural)
            workzone_id: Workzone donde se desplegará
            author_id: ID del instructor que solicita la generación
            complexity: "standard" (sonnet) o "complex" (opus)

        Returns:
            dict con el escenario generado y validado, o errores
        """
        # 1. Seleccionar agente según complejidad
        agent = (
            complex_scenario_agent if complexity == "complex"
            else scenario_agent
        )

        # 2. Construir el prompt contextualizado
        prompt = self._build_generation_prompt(description, workzone_id)

        # 3. Ejecutar el agente (incluye tool-use iterativo)
        result = await Runner.run(
            agent,
            prompt,
        )

        # 4. Extraer el JSON del resultado
        scenario_data = self._extract_scenario_json(result.final_output)

        # 5. Validar contra infraestructura real
        validation = await self.validator.validate(scenario_data, workzone_id)

        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
                "scenario_draft": scenario_data,
                "message": "El escenario generado no pasó la validación"
            }

        # 6. Almacenar en base de datos
        db = next(get_db())
        template = ScenarioTemplate(
            name=scenario_data["name"],
            description=scenario_data["description"],
            category=scenario_data["category"],
            difficulty=scenario_data["difficulty"],
            topology_config=scenario_data["topology_config"],
            vm_configs=scenario_data["vm_configs"],
            network_configs=scenario_data["network_configs"],
            security_configs=scenario_data.get("security_configs"),
            author_id=author_id,
            is_public=False,  # Siempre privado hasta revisión humana
            tags=scenario_data.get("tags", []),
            estimated_deploy_time=scenario_data.get("estimated_deploy_time", 15),
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        return {
            "success": True,
            "template_id": template.id,
            "scenario": scenario_data,
            "validation": validation,
            "message": f"Escenario '{template.name}' generado y almacenado"
        }

    def _build_generation_prompt(self, description: str, workzone_id: int) -> str:
        """
        Construye el prompt con contexto de la workzone y el catálogo.
        No incluimos todo el catálogo en el prompt: el agente lo consulta
        con sus herramientas. Solo pasamos la información de la workzone
        para que el agente sepa los límites.
        """
        db = next(get_db())
        wz = db.query(Workzone).filter(Workzone.id == workzone_id).first()

        return f"""Genera un escenario de ciberejercicio basado en esta descripción:

DESCRIPCIÓN DEL INSTRUCTOR:
{description}

CONTEXTO DE LA WORKZONE:
- ID: {workzone_id}
- Límite CPU: {wz.cpu_limit or 32} cores
- Límite RAM: {wz.memory_limit or 65536} MB
- Límite disco: {wz.storage_limit or 500} GB
- VLAN base: {wz.vlan_id or 'no asignada'}

INSTRUCCIONES:
1. Primero, consulta los templates de VM disponibles con list_vm_templates().
2. Consulta los playbooks disponibles con list_available_playbooks().
3. Diseña la topología y selecciona VMs del catálogo real.
4. Valida la configuración de red con validate_network_config().
5. Verifica que los recursos caben con check_resource_availability().
6. Genera el JSON completo del escenario."""

    def _extract_scenario_json(self, agent_output: str) -> dict:
        """Extrae el JSON del output del agente, manejando texto envolvente."""
        # El agente puede devolver texto antes/después del JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', agent_output)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("El agente no generó un JSON válido")
