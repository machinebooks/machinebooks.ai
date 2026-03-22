# Extraído de: LibroCyberrange/cap-19-red-blue-ia.md
# Ejemplo didáctico: patrones/ai_service/purple_team_orchestrator.py
import asyncio
from datetime import datetime

class PurpleTeamOrchestrator:
    """
    Orquesta un ejercicio purple team con:
    - Agente red team autónomo (ataca)
    - Asistente blue team (ayuda al defensor humano)
    - Sistema de scoring y telemetría
    """

    def __init__(
        self,
        scenario_id: str,
        workzone_id: str,
        red_config: RedTeamConfig,
        difficulty: str = "intermediate"
    ):
        self.scenario_id = scenario_id
        self.workzone_id = workzone_id

        # Inicializar agente red team
        self.red_agent = RedTeamAgent(
            config=red_config,
            state=CampaignState(
                scenario_id=scenario_id,
                workzone_id=workzone_id
            )
        )

        # Inicializar asistente blue team
        self.blue_assistant = BlueTeamAssistant(
            scenario_id=scenario_id,
            workzone_id=workzone_id
        )

        # Telemetría del ejercicio
        self.telemetry_log: list[dict] = []
        self.scoring = PurpleTeamScoring()
        self.start_time: datetime = None
        self.is_active: bool = False

    async def start_exercise(self):
        """Inicia el ejercicio purple team."""
        self.start_time = datetime.utcnow()
        self.is_active = True

        # Ejecutar el bucle del red team en background
        # El blue team es reactivo — responde a consultas
        red_team_task = asyncio.create_task(
            self._red_team_loop()
        )

        # Monitor de alertas que alimenta al blue team
        alert_monitor_task = asyncio.create_task(
            self._alert_monitor_loop()
        )

        return {
            "status": "started",
            "scenario_id": self.scenario_id,
            "start_time": self.start_time.isoformat()
        }

    async def _red_team_loop(self):
        """
        Bucle principal del red team.
        Ejecuta un paso cada N segundos según la velocidad configurada.
        """
        speed_delays = {"slow": 60, "normal": 30, "fast": 10}
        delay = speed_delays.get(
            self.red_agent.config.attack_speed, 30
        )

        while self.is_active:
            try:
                # Ejecutar siguiente paso de la campaña
                result = await self.red_agent.execute_step()

                # Registrar en telemetría (esto genera las alertas
                # que el SIEM captura y el blue team analiza)
                self._record_telemetry(
                    source="red_team",
                    data=result
                )

                # Actualizar scoring
                self.scoring.update_red_progress(result)

                # Notificar al frontend vía WebSocket
                await self._notify_exercise_update(
                    event_type="red_team_action",
                    data=self._sanitize_for_blue(result)
                )

                # Verificar si la campaña terminó
                if self._campaign_complete():
                    break

                # Esperar antes del siguiente paso
                await asyncio.sleep(delay)

            except Exception as e:
                self._record_telemetry(
                    source="red_team_error",
                    data={"error": str(e)}
                )

    async def _alert_monitor_loop(self):
        """
        Monitoriza alertas del SIEM y las procesa
        con el asistente blue team.
        """
        while self.is_active:
            # Obtener alertas nuevas del SIEM
            new_alerts = await self._fetch_new_siem_alerts()

            for alert in new_alerts:
                # Análisis rápido automático de cada alerta
                analysis = await self.blue_assistant.analyze_alert(alert)

                # Enviar análisis al defensor vía WebSocket
                await self._notify_exercise_update(
                    event_type="alert_analysis",
                    data={
                        "alert": alert,
                        "analysis": analysis["analysis"],
                        "recommended_actions": self._extract_recommendations(
                            analysis
                        )
                    }
                )

                # Registrar en telemetría
                self._record_telemetry(
                    source="blue_assistant",
                    data=analysis
                )

            await asyncio.sleep(5)  # Polling cada 5 segundos

    def _sanitize_for_blue(self, red_result: dict) -> dict:
        """
        Elimina información del red team que el blue no debe ver.
        Solo pasa lo que generaría un adversario real: artefactos
        de red, logs de sistema, indicadores observables.
        """
        # El blue team NO ve el razonamiento del red team,
        # ni las herramientas usadas, ni los objetivos pendientes.
        # Solo ve los efectos: alertas del SIEM, tráfico de red,
        # eventos de sistema.
        return {"event": "new_siem_alerts_available"}

    async def stop_exercise(self) -> dict:
        """Detiene el ejercicio y genera informe."""
        self.is_active = False

        # Generar timeline del incidente
        timeline = await self.blue_assistant.generate_incident_timeline()

        # Calcular scoring final
        final_score = self.scoring.calculate_final(
            red_objectives_completed=len(
                self.red_agent.state.objectives_completed
            ),
            red_objectives_total=len(
                self.red_agent.config.objectives
            ),
            blue_detections=self.scoring.blue_detections,
            blue_response_times=self.scoring.response_times,
            exercise_duration=(
                datetime.utcnow() - self.start_time
            ).total_seconds()
        )

        # Generar dataset etiquetado para entrenamiento de modelos
        labeled_dataset = self._generate_labeled_dataset()

        return {
            "timeline": timeline,
            "scoring": final_score,
            "telemetry_events": len(self.telemetry_log),
            "labeled_dataset_size": len(labeled_dataset),
            "red_team_summary": {
                "techniques_used": self.red_agent.state.mitre_techniques_used,
                "hosts_compromised": len(
                    self.red_agent.state.compromised_hosts
                ),
                "objectives_completed": len(
                    self.red_agent.state.objectives_completed
                )
            }
        }

    def _generate_labeled_dataset(self) -> list[dict]:
        """
        Genera un dataset etiquetado a partir de la telemetría
        del ejercicio. Cada evento tiene:
        - Los datos raw (como los vería un SIEM real)
        - La etiqueta: benigno / malicioso
        - La técnica MITRE ATT&CK si es malicioso
        - El contexto de la cadena de ataque

        Este dataset alimenta el entrenamiento de modelos
        de detección y clasificación.
        """
        dataset = []
        for event in self.telemetry_log:
            labeled_event = {
                "raw_data": event.get("observable_data"),
                "timestamp": event.get("timestamp"),
                "label": (
                    "malicious" if event.get("source") == "red_team"
                    else "benign"
                ),
                "mitre_technique": event.get("technique_id"),
                "attack_phase": event.get("phase"),
                "confidence": 1.0  # Etiqueta ground-truth
            }
            dataset.append(labeled_event)
        return dataset
