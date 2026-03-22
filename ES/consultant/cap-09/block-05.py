# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
import json
from pathlib import Path

@dataclass
class RegistroPropuesta:
    id_propuesta: str
    cliente: str
    fecha_generacion: datetime
    secciones: list[SeccionGenerada]
    coste_total_ia: float
    horas_humanas: float           # Se registra al finalizar
    resultado: str | None = None   # "ganada", "perdida", "desierta"
    puntuacion_tecnica: float | None = None

    def guardar(self, directorio: Path) -> None:
        """Persiste el registro para análisis posterior."""
        ruta = directorio / f"{self.id_propuesta}.json"
        data = {
            "id": self.id_propuesta,
            "cliente": self.cliente,
            "fecha": self.fecha_generacion.isoformat(),
            "coste_ia": self.coste_total_ia,
            "horas_humanas": self.horas_humanas,
            "resultado": self.resultado,
            "puntuacion_tecnica": self.puntuacion_tecnica,
            "secciones": [
                {
                    "tipo": s.tipo.value,
                    "version_final": s.version,
                    "score_quality": s.score_quality,
                    "tokens": s.tokens_consumidos,
                    "coste": s.coste_generacion,
                    "notas_revision": s.notas_revision
                }
                for s in self.secciones
            ],
            "metricas": {
                "ratio_horas": self.horas_humanas / 120,  # vs baseline
                "coste_por_seccion": self.coste_total_ia / len(self.secciones),
                "score_medio": sum(s.score_quality for s in self.secciones)
                               / len(self.secciones)
            }
        }
        ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def calcular_roi(self) -> dict:
        """Calcula ROI de la generación asistida."""
        horas_baseline = 120  # Horas sin asistencia de IA
        coste_hora_senior = 95.0  # EUR/hora (escalado)
        ahorro_horas = horas_baseline - self.horas_humanas
        ahorro_eur = ahorro_horas * coste_hora_senior
        roi = ahorro_eur / (self.coste_total_ia * 0.92)  # USD→EUR aprox
        return {
            "horas_ahorradas": ahorro_horas,
            "ahorro_estimado_eur": ahorro_eur,
            "coste_ia_eur": self.coste_total_ia * 0.92,
            "roi_x": round(roi, 1)
        }
