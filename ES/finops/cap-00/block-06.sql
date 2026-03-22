# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
-- Coste por servicio en el ultimo mes
SELECT
    line_item_product_code AS servicio,
    SUM(line_item_unblended_cost) AS coste_total
FROM cur_database.cur_table
WHERE year = '2026' AND month = '03'
GROUP BY line_item_product_code
ORDER BY coste_total DESC
LIMIT 20;
