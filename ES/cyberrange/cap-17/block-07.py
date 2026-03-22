# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/scenario_validator.py
import ipaddress
from backend.models import VMTemplate, Workzone, CtfFlag
from backend.database import get_db

class ScenarioValidator:
    """
    Valida que un escenario generado por IA cumple todas las
    restricciones de la infraestructura real.

    Esta capa es CRÍTICA: es la barrera entre lo que el LLM
    genera (optimista, a veces incorrecto) y lo que se despliega
    (debe funcionar sin excepción).
    """

    async def validate(self, scenario_data: dict, workzone_id: int) -> dict:
        """Ejecuta todas las validaciones y devuelve resultado agregado."""
        errors = []
        warnings = []

        # 1. Validar estructura JSON
        errors.extend(self._validate_schema(scenario_data))

        # 2. Validar que los templates de VM existen
        errors.extend(self._validate_templates(scenario_data))

        # 3. Validar configuración de red
        errors.extend(self._validate_networks(scenario_data))

        # 4. Validar recursos contra workzone
        errors.extend(self._validate_resources(scenario_data, workzone_id))

        # 5. Validar unicidad de flags
        errors.extend(self._validate_flags(scenario_data))

        # 6. Validar mapping MITRE
        warnings.extend(self._validate_mitre(scenario_data))

        # 7. Validar coherencia de dificultad
        warnings.extend(self._validate_difficulty_coherence(scenario_data))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _validate_templates(self, scenario_data: dict) -> list:
        """Verifica que cada template_id referenciado existe en Proxmox."""
        errors = []
        db = next(get_db())

        for vm in scenario_data.get("vm_configs", []):
            template_id = vm.get("template_id")
            if template_id:
                exists = db.query(VMTemplate).filter(
                    VMTemplate.id == template_id
                ).first()
                if not exists:
                    errors.append(
                        f"Template ID {template_id} para nodo "
                        f"'{vm.get('node_id')}' no existe en el catálogo"
                    )
        return errors

    def _validate_networks(self, scenario_data: dict) -> list:
        """Verifica que los rangos de red no colisionan."""
        errors = []
        db = next(get_db())
        topology = scenario_data.get("topology_config", {})

        networks = topology.get("networks", [])

        # Verificar colisiones entre redes del escenario
        for i, net_a in enumerate(networks):
            try:
                cidr_a = ipaddress.ip_network(net_a["cidr"], strict=False)
            except (ValueError, KeyError) as e:
                errors.append(f"Red '{net_a.get('id')}': CIDR inválido — {e}")
                continue

            for net_b in networks[i+1:]:
                try:
                    cidr_b = ipaddress.ip_network(net_b["cidr"], strict=False)
                    if cidr_a.overlaps(cidr_b):
                        errors.append(
                            f"Redes '{net_a['id']}' ({net_a['cidr']}) y "
                            f"'{net_b['id']}' ({net_b['cidr']}) se solapan"
                        )
                except (ValueError, KeyError):
                    pass  # Ya se reportó arriba

        # Verificar colisiones con workzones activas
        active_zones = db.query(Workzone).filter(
            Workzone.network_cidr.isnot(None),
            Workzone.status == "active"
        ).all()

        for net in networks:
            try:
                cidr = ipaddress.ip_network(net["cidr"], strict=False)
                for zone in active_zones:
                    existing = ipaddress.ip_network(
                        zone.network_cidr, strict=False
                    )
                    if cidr.overlaps(existing):
                        errors.append(
                            f"Red '{net['id']}' ({net['cidr']}) colisiona "
                            f"con workzone '{zone.name}' ({zone.network_cidr})"
                        )
            except (ValueError, KeyError):
                pass

        return errors

    def _validate_resources(self, scenario_data: dict, workzone_id: int) -> list:
        """Verifica que la workzone tiene capacidad para el escenario."""
        errors = []
        db = next(get_db())
        wz = db.query(Workzone).filter(Workzone.id == workzone_id).first()

        if not wz:
            return [f"Workzone {workzone_id} no encontrada"]

        total_cpu = sum(vm.get("cpu", 2) for vm in scenario_data.get("vm_configs", []))
        total_ram = sum(vm.get("ram_mb", 2048) for vm in scenario_data.get("vm_configs", []))
        total_disk = sum(vm.get("disk_gb", 20) for vm in scenario_data.get("vm_configs", []))

        if total_cpu > (wz.cpu_limit or 32):
            errors.append(
                f"CPU total ({total_cpu} cores) excede límite "
                f"de workzone ({wz.cpu_limit} cores)"
            )
        if total_ram > (wz.memory_limit or 65536):
            errors.append(
                f"RAM total ({total_ram} MB) excede límite "
                f"de workzone ({wz.memory_limit} MB)"
            )

        return errors

    def _validate_flags(self, scenario_data: dict) -> list:
        """Verifica unicidad de flags y formato correcto."""
        errors = []
        flags = scenario_data.get("flags", [])

        if len(flags) == 0:
            errors.append("El escenario no define ninguna flag")
            return errors

        flag_ids = [f.get("id") for f in flags]
        if len(flag_ids) != len(set(flag_ids)):
            errors.append("Hay flag IDs duplicados en el escenario")

        # Verificar que cada flag tiene los campos mínimos
        for flag in flags:
            if not flag.get("description"):
                errors.append(f"Flag '{flag.get('id')}' sin descripción")
            if not flag.get("points"):
                errors.append(f"Flag '{flag.get('id')}' sin puntos asignados")
            if not flag.get("technique"):
                errors.append(f"Flag '{flag.get('id')}' sin técnica MITRE")

        return errors

    def _validate_difficulty_coherence(self, scenario_data: dict) -> list:
        """
        Verifica que la dificultad declarada es coherente con
        las técnicas incluidas. Un escenario 'beginner' no debería
        incluir Golden Ticket o DCSync.
        """
        warnings = []
        difficulty = scenario_data.get("difficulty", "intermediate")

        advanced_techniques = {
            "T1003.006",   # DCSync
            "T1558.001",   # Golden Ticket
            "T1550.002",   # Pass the Hash
            "T1187",       # Forced Authentication (NTLM relay)
        }

        beginner_incompatible = {
            "T1003.006", "T1558.001", "T1550.002", "T1187"
        }

        if difficulty in ("beginner", "intermediate"):
            mitre = scenario_data.get("mitre_mapping", [])
            for entry in mitre:
                tech_id = entry.get("technique_id", "")
                if tech_id in beginner_incompatible and difficulty == "beginner":
                    warnings.append(
                        f"Técnica {tech_id} ({entry.get('name')}) es avanzada "
                        f"para dificultad '{difficulty}'"
                    )

        return warnings

    def _validate_schema(self, data: dict) -> list:
        """Verifica campos obligatorios."""
        errors = []
        required = ["name", "category", "difficulty", "topology_config", "vm_configs"]
        for field in required:
            if field not in data:
                errors.append(f"Campo obligatorio ausente: '{field}'")
        return errors

    def _validate_mitre(self, data: dict) -> list:
        """Verifica que las técnicas MITRE referenciadas son válidas."""
        warnings = []
        # Lista simplificada de técnicas válidas (en producción se consultaría
        # la base de datos de MITRE ATT&CK completa)
        for entry in data.get("mitre_mapping", []):
            tech_id = entry.get("technique_id", "")
            if not tech_id.startswith("T"):
                warnings.append(f"Técnica MITRE con formato inválido: '{tech_id}'")
        return warnings
