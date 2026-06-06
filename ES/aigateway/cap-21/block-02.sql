# Extraído de: LibroAIGateway/cap-21-audit-append-only.md
CREATE TRIGGER trg_audit_logs_no_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
BEGIN
  IF NOT (
    OLD.chain_hash IS NULL AND NEW.chain_hash IS NOT NULL
    AND OLD.id <=> NEW.id
    AND OLD.request_id <=> NEW.request_id
    AND OLD.prompt_hash <=> NEW.prompt_hash
    -- ... todas las demás columnas iguales ...
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'audit_logs is append-only';
  END IF;
END;
