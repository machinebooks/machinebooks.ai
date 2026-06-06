# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Combinación de score (gateway/app/services/jailbreak_detector.py:207-210)
for rule in _RULES:
    m = rule.pattern.search(scan_text)
    if m:
        matches.append(Match(...))
        # Mejor peso por categoría — no acumula dentro de la misma
        cat_best_weight[rule.category] = max(
            cat_best_weight.get(rule.category, 0), rule.weight)

score = min(100, sum(cat_best_weight.values()))
