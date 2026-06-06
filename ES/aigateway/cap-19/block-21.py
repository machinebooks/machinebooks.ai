# Extraído de: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Pipeline placement (pipeline/stages/security_input.py)
# auth -> hooks.pre_chat -> security_input -> filter -> hooks.pii_detected
# -> reduce -> route -> enrich -> route.finalize -> ...

async def run(ctx) -> bool:
    # 1. MSJ defense — prefill + many-shot scan
    msj_result = MSJDefenseService.check_all(msg_dicts, thresholds)

    # 2. Content classifier — 15 categorías
    classification = await ContentClassifierService.classify(full_prompt, ...)

    # 3. Leak detection — credenciales extra + reconnaissance behavioral
    leak_scan = await LeakDetectionService.scan_input(full_prompt, redis, device_id)

    # 4. Jailbreak detector v2 — scoring NFKC con bypass por dispositivo
    jb_evidence = jailbreak_detector.detect(full_prompt, threshold=...)
    jb_result = jailbreak_detector.enforce(full_prompt, action_mode=..., bypass=...)

    # 5. Guardrails configurables (BD) — complementa hardcoded con reglas tuneables
    redacted = await guardrail_service.evaluate(db, text=content, direction="input", ...)
