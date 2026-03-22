# Extraído de: LibroDevSecOps/cap-02-anatomia-vulnerabilidad.md
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/api/reports/export", methods=["GET"])
def export_reports():
    """Exporta informes filtrados por categoría."""
    category = request.args.get("category", "")

    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()

    # VULNERABLE: concatenación directa de input del usuario
    query = f"SELECT id, title, created_at FROM reports WHERE category = '{category}'"
    cursor.execute(query)

    rows = cursor.fetchall()
    results = [
        {"id": r[0], "title": r[1], "created_at": r[2]}
        for r in rows
    ]
    conn.close()
    return jsonify(results)
