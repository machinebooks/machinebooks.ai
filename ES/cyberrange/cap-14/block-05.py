# Extraído de: LibroCyberrange/cap-14-equipos-competicion.md
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=130)
    max_members: int = Field(5, ge=1, le=20)

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError(
                "El nombre solo puede contener letras, números, "
                "espacios, guiones y guiones bajos"
            )
        return v
