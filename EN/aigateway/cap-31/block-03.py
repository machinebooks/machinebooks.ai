# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Anti-farming: unique sha256 per (challenge_id, user_id) — gateway/app/api/v1/challenges.py
# Mode A (transcript): resubmission of the same work is blocked
sha = hashlib.sha256(transcript.encode()).hexdigest()
existing = await db.execute(
    text("SELECT id FROM challenge_attempts "
         "WHERE user_id=:uid AND challenge_id=:cid "
         "AND transcript_sha=:sha LIMIT 1"),
    {"uid": uid, "cid": ch.id, "sha": sha},
)
if existing.first():
    raise HTTPException(409, "Ya enviaste este trabajo para este reto.")
