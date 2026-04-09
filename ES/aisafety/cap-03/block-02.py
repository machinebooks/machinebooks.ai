# Extraido de: LibroAISafety/cap-03-dentro-del-modelo.md
# Análisis de logprobs para detectar fuga de información
# Ejemplo didáctico con la API de un proveedor que expone logprobs

def analizar_incertidumbre(response) -> dict:
    """Analiza las probabilidades de tokens para detectar
    patrones que indiquen que el modelo 'sabe' algo que
    está intentando no decir."""
    tokens_analisis = []

    for token_info in response.logprobs:
        prob_elegido = token_info["probability"]
        # Si el token elegido tiene baja probabilidad,
        # el modelo estaba "dudando" — posible señal de
        # conflicto entre conocimiento y restricciones
        if prob_elegido < 0.3:
            # Examinar las alternativas descartadas
            alternativas = token_info.get("top_alternatives", [])
            tokens_analisis.append({
                "token": token_info["token"],
                "prob": prob_elegido,
                "alternativas": alternativas,
                # Alta entropía + restricción activa =
                # el modelo sabe la respuesta pero intenta no darla
                "posible_supresion": len(alternativas) > 5
                    and prob_elegido < 0.15
            })

    return {
        "tokens_analizados": len(tokens_analisis),
        "posibles_supresiones": sum(
            1 for t in tokens_analisis if t["posible_supresion"]
        )
    }
