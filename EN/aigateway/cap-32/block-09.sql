# Extracted from: LibroAIGateway/cap-32-data-model.md
-- NNN_description.sql
-- Comment: what changes and why

SET NAMES utf8mb4;

-- 1. Structure (tables/columns)
ALTER TABLE existing_table
    ADD COLUMN IF NOT EXISTS new_col VARCHAR(100) NULL;

-- 2. Data (backfill if applicable)
UPDATE existing_table SET new_col = 'default' WHERE new_col IS NULL;

-- 3. Indexes
CREATE INDEX IF NOT EXISTS idx_table_col ON existing_table (new_col);

-- 4. Triggers (if applicable)
DROP TRIGGER IF EXISTS trg_name;
CREATE TRIGGER trg_name BEFORE UPDATE ON existing_table
FOR EACH ROW BEGIN /* ... */ END//
