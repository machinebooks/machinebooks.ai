# Extraído de: LibroDevSecOps/cap-02-anatomia-vulnerabilidad.md
@app.route("/api/reports/export", methods=["GET"])
def export_reports():
    """Exporta informes filtrados por categoría — versión segura."""
    category = request.args.get("category", "")

    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()

    # SEGURO: consulta parametrizada con placeholder
    query = "SELECT id, title, created_at FROM reports WHERE category = ?"
    cursor.execute(query, (category,))

    rows = cursor.fetchall()
    results = [
        {"id": r[0], "title": r[1], "created_at": r[2]}
        for r in rows
    ]
    conn.close()
    return jsonify(results)
