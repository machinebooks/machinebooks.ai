# Extraído de: LibroConsultor/cap-14-reporting.md
import asyncio
from pathlib import Path

async def generar_informe_completo(
    proyecto: ProyectoReporting,
    config: dict
) -> dict[str, str]:
    """Orquesta la generación completa del informe."""

    voice = config["voice_prompt"]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fase 1: Generar narrativas de hallazgos en paralelo
    narrativas = await asyncio.gather(*[
        asyncio.to_thread(
            generar_narrativa_hallazgo, h, proyecto.alcance, voice
        )
        for h in proyecto.hallazgos
    ])

    # Construir sección de hallazgos
    seccion_hallazgos = "\n\n---\n\n".join(
        f"### Hallazgo {h.id}: {h.titulo}\n\n"
        f"**Severidad:** {h.severidad.value.upper()} | "
        f"**Área:** {h.area}\n\n{narrativa}"
        for h, narrativa in zip(proyecto.hallazgos, narrativas)
    )

    secciones = {"hallazgos": seccion_hallazgos}

    # Fase 2: Generar análisis y recomendaciones
    secciones["analisis"] = generar_seccion_analisis(
        proyecto, secciones, voice
    )
    secciones["recomendaciones"] = priorizar_recomendaciones(
        proyecto.hallazgos,
        config.get("presupuesto_cliente", "No definido"),
        config.get("restricciones", "Ninguna especificada"),
        voice
    )

    # Fase 3: Generar resumen ejecutivo (necesita secciones previas)
    secciones["resumen_ejecutivo"] = generar_resumen_ejecutivo(
        proyecto, secciones, voice
    )

    # Fase 4: Ensamblar Markdown completo
    markdown_completo = ensamblar_markdown(proyecto, secciones)
    md_path = output_dir / f"{proyecto.nombre_proyecto}.md"
    md_path.write_text(markdown_completo, encoding="utf-8")

    # Fase 5: Exportar formatos en paralelo
    word_path = output_dir / f"{proyecto.nombre_proyecto}.docx"
    pptx_path = output_dir / f"{proyecto.nombre_proyecto}_exec.pptx"
    onepager_path = output_dir / f"{proyecto.nombre_proyecto}_CEO.docx"

    top_5 = sorted(
        proyecto.hallazgos,
        key=lambda h: list(Severidad).index(h.severidad)
    )[:5]

    await asyncio.gather(
        asyncio.to_thread(
            exportar_word, str(md_path), str(word_path),
            config["reference_docx"]
        ),
        asyncio.to_thread(
            generar_presentacion_ejecutiva,
            proyecto, secciones["resumen_ejecutivo"], top_5,
            secciones["recomendaciones"],
            config["plantilla_pptx"], str(pptx_path)
        ),
        asyncio.to_thread(
            generar_one_pager, proyecto,
            secciones["resumen_ejecutivo"], top_5,
            str(onepager_path), config["plantilla_onepager"]
        ),
    )

    return {
        "markdown": str(md_path),
        "word": str(word_path),
        "presentacion": str(pptx_path),
        "one_pager": str(onepager_path),
    }
