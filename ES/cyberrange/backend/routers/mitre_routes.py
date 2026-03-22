# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/mitre_routes.py — Esquemas Pydantic para MITRE
from pydantic import BaseModel
from typing import List, Optional

class MitreTacticOut(BaseModel):
    tactic_id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True  # Compatibilidad con SQLAlchemy

class MitreTechniqueOut(BaseModel):
    technique_id: str
    name: str
    description: Optional[str] = None
    platforms: Optional[List[str]] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True

class ChallengeMitreIn(BaseModel):
    challenge_id: int
    technique_id: Optional[str] = None
    subtechnique_id: Optional[str] = None
    skill_level: SkillLevel = SkillLevel.beginner
