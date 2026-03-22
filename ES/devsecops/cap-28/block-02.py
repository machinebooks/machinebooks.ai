# Extraído de: LibroDevSecOps/cap-28-caso-compliance.md
def generar_informe_auditoria(resultados_controles: dict,
                               client: anthropic.Anthropic):
    """Genera informe de compliance ENS en formato Markdown
    legible para auditores no técnicos."""

    prompt = f"""Genera un informe de compliance ENS nivel alto
a partir de los siguientes resultados de evaluación de controles.

{json.dumps(resultados_controles, indent=2, ensure_ascii=False)}

El informe debe seguir esta estructura:
1. Resumen ejecutivo: controles conformes / parciales / no conformes
2. Marco operacional: tabla con cada control, estado y evidencia
3. Marco de protección: tabla con cada control, estado y evidencia
4. Hallazgos y acciones pendientes: detalle de no conformidades
5. Conclusión: valoración global de postura de cumplimiento

Tono: técnico pero accesible para un auditor de seguridad
que no es desarrollador. Referenciar los artefactos por nombre
y fecha. NO inventar evidencias ni hallazgos que no estén
en los datos proporcionados."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def ejecutar_compliance_completo(bucket_path: str):
    """Orquesta la evaluación completa de compliance ENS."""
    client = anthropic.Anthropic()

    # 1. Recopilar evidencias de los últimos 90 días
    evidencias = recopilar_evidencias(bucket_path, periodo_dias=90)

    # 2. Evaluar cada control
    resultados = {}
    for control_id, control_def in ENS_CONTROL_MAP.items():
        resultados[control_id] = evaluar_control(
            control_id, control_def, evidencias, client
        )

    # 3. Generar informe
    informe = generar_informe_auditoria(resultados, client)

    # 4. Guardar con metadatos
    fecha = datetime.now().strftime("%Y-%m-%d")
    Path(f"informes/compliance-ens-{fecha}.md").write_text(
        informe, encoding="utf-8"
    )

    # 5. Resumen de resultados
    conformes = sum(
        1 for r in resultados.values()
        if r["estado"] == "conforme"
    )
    parciales = sum(
        1 for r in resultados.values()
        if r["estado"] == "parcial"
    )
    no_conformes = sum(
        1 for r in resultados.values()
        if r["estado"] == "no_conforme"
    )
    print(f"Compliance ENS: {conformes} conformes, "
          f"{parciales} parciales, {no_conformes} no conformes "
          f"de {len(resultados)} controles evaluados")
