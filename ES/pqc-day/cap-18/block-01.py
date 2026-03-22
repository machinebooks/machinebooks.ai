# Extraído de: LibroPQC/cap-18-roadmap.md
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


class ActionManager:
    """
    Gestiona las acciones de remediación derivadas de hallazgos
    criptográficos priorizados.
    """

    # Mapeo de prioridad a plazo por defecto (días)
    DEFAULT_DEADLINES = {
        'critical': 14,    # 2 semanas
        'high': 90,        # 1 trimestre
        'medium': 180,     # 6 meses
        'low': 365         # 1 año
    }

    # Mapeo de prioridad a esfuerzo estimado por defecto
    DEFAULT_EFFORT = {
        'critical': '1-2 semanas',
        'high': '2-4 semanas',
        'medium': '1-2 meses',
        'low': '2-4 meses'
    }

    def generate_actions_from_findings(
        self,
        assessment_id: int,
        prioritized_findings: List[dict],
        db_session
    ) -> List[dict]:
        """
        Genera acciones de remediación a partir de hallazgos priorizados.

        Agrupa hallazgos por patrón común (misma biblioteca,
        mismo servicio, misma dependencia) para evitar crear
        una acción por cada línea de código afectada.
        """
        # Agrupar hallazgos por clave de migración
        migration_groups = self._group_by_migration_key(prioritized_findings)
        actions_created = []

        for group_key, group_findings in migration_groups.items():
            # La prioridad del grupo es la máxima de sus hallazgos
            max_priority = max(
                f['priority_label'] for f in group_findings
            )
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            max_priority = max(
                group_findings,
                key=lambda f: priority_order.get(f['priority_label'], 0)
            )['priority_label']

            # Calcular fecha límite basada en prioridad
            deadline_days = self.DEFAULT_DEADLINES.get(max_priority, 180)
            due_date = datetime.utcnow().date() + timedelta(days=deadline_days)

            action = {
                'assessment_id': assessment_id,
                'title': self._generate_action_title(group_key, group_findings),
                'description': self._generate_action_description(
                    group_key, group_findings
                ),
                'priority': max_priority,
                'status': 'pending',
                'due_date': due_date,
                'estimated_effort': self.DEFAULT_EFFORT.get(
                    max_priority, '1-2 meses'
                ),
                'affected_findings': len(group_findings),
                'affected_files': list(set(
                    f.get('file_path', '') for f in group_findings
                ))
            }
            actions_created.append(action)

        return sorted(
            actions_created,
            key=lambda a: priority_order.get(a['priority'], 0),
            reverse=True
        )

    def _group_by_migration_key(
        self, findings: List[dict]
    ) -> Dict[str, List[dict]]:
        """
        Agrupa hallazgos por clave de migración.

        La clave combina el algoritmo detectado con el tipo
        de uso (autenticación, cifrado, firma, protocolo).
        Hallazgos con la misma clave se resuelven con la
        misma acción de migración.
        """
        groups: Dict[str, List[dict]] = {}
        for finding in findings:
            algo = finding.get('algorithm', 'unknown')
            usage = finding.get('usage_context', 'general')
            # Normalizar: RSA en JWT y RSA en certificados
            # son migraciones diferentes
            key = f"{algo}:{usage}"
            groups.setdefault(key, []).append(finding)
        return groups

    def _generate_action_title(
        self, group_key: str, findings: List[dict]
    ) -> str:
        """Genera un título descriptivo para la acción"""
        algo, usage = group_key.split(':', 1)
        count = len(findings)
        return (
            f"Migrar {algo.upper()} en contexto {usage} "
            f"({count} hallazgo{'s' if count > 1 else ''})"
        )

    def _generate_action_description(
        self, group_key: str, findings: List[dict]
    ) -> str:
        """Genera una descripción con ficheros afectados y recomendación"""
        algo, usage = group_key.split(':', 1)
        files = set(f.get('file_path', 'N/A') for f in findings)

        # Recomendación de algoritmo PQC según uso
        pqc_recommendation = self._get_pqc_recommendation(algo, usage)

        desc = f"Reemplazar {algo.upper()} por {pqc_recommendation} "
        desc += f"en {len(files)} fichero(s):\n"
        for f in sorted(files)[:10]:  # Limitar a 10 ficheros
            desc += f"  - {f}\n"
        if len(files) > 10:
            desc += f"  ... y {len(files) - 10} ficheros más\n"
        return desc

    def _get_pqc_recommendation(self, algorithm: str, usage: str) -> str:
        """
        Devuelve el algoritmo PQC recomendado según el uso.

        No es una tabla estática: el contexto importa.
        RSA usado para firma requiere ML-DSA; RSA usado
        para intercambio de claves requiere ML-KEM.
        """
        recommendations = {
            ('rsa', 'key_exchange'): 'ML-KEM (FIPS 203)',
            ('rsa', 'signature'): 'ML-DSA (FIPS 204)',
            ('rsa', 'authentication'): 'ML-DSA (FIPS 204)',
            ('rsa', 'encryption'): 'ML-KEM (FIPS 203)',
            ('ecdsa', 'signature'): 'ML-DSA (FIPS 204)',
            ('ecdsa', 'authentication'): 'ML-DSA (FIPS 204)',
            ('ecdh', 'key_exchange'): 'ML-KEM (FIPS 203)',
            ('dh', 'key_exchange'): 'ML-KEM (FIPS 203)',
            ('dsa', 'signature'): 'ML-DSA (FIPS 204)',
        }
        key = (algorithm.lower(), usage.lower())
        return recommendations.get(
            key,
            'ML-KEM/ML-DSA (consultar contexto específico)'
        )
