# Extracted from: LibroAIGateway/cap-32-data-model.md
-- Simplified example of the calculation (done in Python, periodic worker):
-- chain_hash[N] = SHA-256(id || prompt_hash || cost_usd || chain_hash[N-1])
-- chain_hash[0]  = SHA-256(id || prompt_hash || cost_usd || 'genesis')
-- If chain_hash[N] != expected hash → someone tampered with audit_logs between N and the last seal.
