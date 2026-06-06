# Extraído de: LibroAIGateway/cap-32-modelo-de-datos.md
-- NNN_descripcion.sql
-- Comentario: qué cambia y por qué

SET NAMES utf8mb4;

-- 1. Estructura (tablas/columnas)
ALTER TABLE existing_table
    ADD COLUMN IF NOT EXISTS new_col VARCHAR(100) NULL;

-- 2. Datos (backfill si aplica)
UPDATE existing_table SET new_col = 'default' WHERE new_col IS NULL;

-- 3. Índices
CREATE INDEX IF NOT EXISTS idx_table_col ON existing_table (new_col);

-- 4. Triggers (si aplica)
DROP TRIGGER IF EXISTS trg_name;
CREATE TRIGGER trg_name BEFORE UPDATE ON existing_table
FOR EACH ROW BEGIN /* ... */ END//
