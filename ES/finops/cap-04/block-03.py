# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# Ejemplo del antipatrón — instrumentación inline
response = await client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=messages
)

# Estas líneas se repiten en cada punto de integración
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
cost = (input_tokens / 1_000_000) * 3.00 + (output_tokens / 1_000_000) * 15.00
await save_usage_log(service="document_analysis", cost=cost, ...)
