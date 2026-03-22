# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# api/tco_routes.py
# Endpoint para consultar el TCO de un proyecto.
# Solo accesible para roles con permiso "finops:read".

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional

from services.tco_calculator import TCOCalculator, DesgloseTCO
from dependencies import get_db, require_permission

router = APIRouter(prefix="/finops/tco", tags=["FinOps TCO"])


@router.get("/{proyecto_codigo}", response_model=dict)
async def get_tco_proyecto(
    proyecto_codigo: str,
    mes_inicio: date,
    mes_fin: date,
    coste_tokens_eur: Optional[float] = 0.0,
    coste_cloud_eur: Optional[float] = 0.0,
    coste_herramientas_eur: Optional[float] = 0.0,
    db: Session = Depends(get_db),
    _: None = Depends(require_permission("finops:read")),
) -> dict:
    """
    Devuelve el TCO completo de un proyecto en un período dado.
    Los costes externos (tokens, cloud) se pasan como query params
    para que el frontend pueda integrar datos de distintas fuentes.
    """
    calculator = TCOCalculator(db)

    desglose = calculator.calcular_tco(
        proyecto_codigo=proyecto_codigo,
        mes_inicio=mes_inicio,
        mes_fin=mes_fin,
        coste_tokens_eur=Decimal(str(coste_tokens_eur)),
        coste_cloud_eur=Decimal(str(coste_cloud_eur)),
        coste_herramientas_eur=Decimal(str(coste_herramientas_eur)),
    )

    return {
        "proyecto": proyecto_codigo,
        "periodo": {"inicio": mes_inicio, "fin": mes_fin},
        "tco_total_eur": float(desglose.coste_total),
        "desglose": {
            "personas_eur": float(desglose.coste_personas_eur),
            "tokens_eur": float(desglose.coste_tokens_eur),
            "cloud_eur": float(desglose.coste_cloud_eur),
            "herramientas_eur": float(desglose.coste_herramientas_eur),
        },
        "ratios": {
            "porcentaje_personas": round(desglose.porcentaje_personas, 1),
            "ratio_personas_vs_ia": round(desglose.ratio_personas_vs_ia, 1),
        },
        "desglose_por_perfil": {
            k: float(v) for k, v in desglose.desglose_por_perfil.items()
        },
    }
