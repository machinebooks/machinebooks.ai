# Extracted from: LibroAIGateway/cap-15-rate-limiting.md
def estimate_tokens_for_request(input_chars: int, max_output_tokens: int = 16_000) -> int:
    """input tokens ≈ chars / 3.5 + prompt base + output reserved."""
    estimated_input = int(input_chars / 3.5) + 500
    return estimated_input + max_output_tokens
