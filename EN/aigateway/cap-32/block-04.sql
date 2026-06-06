# Extracted from: LibroAIGateway/cap-32-data-model.md
CREATE TRIGGER trg_audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
  -- Only allowed mutation: set chain_hash for the first time (seal).
  IF NOT (OLD.chain_hash IS NULL AND NEW.chain_hash IS NOT NULL
          AND OLD.id <=> NEW.id
          AND OLD.prompt_hash <=> NEW.prompt_hash
          AND OLD.cost_usd <=> NEW.cost_usd
          -- ... rest of columns must be identical ...
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'audit_logs is append-only';
  END IF;
END//
