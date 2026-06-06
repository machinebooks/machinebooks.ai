# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
CREATE TRIGGER trg_audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
  -- Única mutación permitida: fijar chain_hash por primera vez (seal).
  IF NOT (OLD.chain_hash IS NULL AND NEW.chain_hash IS NOT NULL
          AND OLD.id <=> NEW.id
          AND OLD.prompt_hash <=> NEW.prompt_hash
          AND OLD.cost_usd <=> NEW.cost_usd
          -- ... resto de columnas deben ser idénticas ...
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'audit_logs is append-only';
  END IF;
END//
