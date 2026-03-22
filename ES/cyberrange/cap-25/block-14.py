# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
@app.get("/ping")
def ping():
    return {"pong": True}
