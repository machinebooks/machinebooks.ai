# Extraído de: LibroAIGateway/cap-31-adopcion-compliance-portal.md
# Anti-farmeo: sha256 único por (challenge_id, user_id) — gateway/app/api/v1/challenges.py
# Modo A (transcript): se bloquea reenvío del mismo trabajo
sha = hashlib.sha256(transcript.encode()).hexdigest()
existing = await db.execute(
    text("SELECT id FROM challenge_attempts "
         "WHERE user_id=:uid AND challenge_id=:cid "
         "AND transcript_sha=:sha LIMIT 1"),
    {"uid": uid, "cid": ch.id, "sha": sha},
)
if existing.first():
    raise HTTPException(409, "Ya enviaste este trabajo para este reto.")
