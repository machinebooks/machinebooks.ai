# Extracted from: LibroAIGateway/cap-22-governance-engine.md
# Functional validators: confirm real checksum
_PII_TYPE_VALIDATORS = {
    "dni": lambda m: is_valid_dni(m) or is_valid_nie(m),
    "nie": is_valid_nie,
    "iban": is_valid_iban,
    "credit_card": is_valid_credit_card,
}
