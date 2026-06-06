# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
-- Ejemplo simplificado del cálculo (realizado en Python, worker periódico):
-- chain_hash[N] = SHA-256(id || prompt_hash || cost_usd || chain_hash[N-1])
-- chain_hash[0]  = SHA-256(id || prompt_hash || cost_usd || 'genesis')
-- Si chain_hash[N] != hash esperado → alguien manipuló audit_logs entre N y el último seal.
