# Extraído de: LibroDevSecOps/cap-01-pipeline-inseguro.md
# Contexto: app/api/search.py, líneas 27-67
@router.get("/search")
async def search_items(
    q: str = Query(..., min_length=1, max_length=200),
    db: Session = Depends(get_db),
):
    # Sanitización de entrada
    sanitized_q = q.replace("'", "''").replace(";", "")

    # HALLAZGO SAST: línea 47
    query = f"SELECT id, name FROM items WHERE name LIKE '%{sanitized_q}%'"
    results = db.execute(text(query)).fetchall()

    return [{"id": r.id, "name": r.name} for r in results]
