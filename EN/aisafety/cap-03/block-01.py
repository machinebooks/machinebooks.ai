# Extracted from: LibroAISafety/ch-03-inside-the-model.md
# Relationship between generation parameters and security
# Example with a generic LLM provider API

# LOW TEMPERATURE (0.0 - 0.3): deterministic responses
# - Security: the model follows instructions more faithfully
# - Risk: if the model has "learned" a harmful pattern,
#   it will reproduce it consistently
# - Use: classification tasks, data extraction,
#   reproducible security evaluations

secure_config = {
    "temperature": 0.1,
    "top_k": 40,
    "top_p": 0.9
}

# HIGH TEMPERATURE (0.7 - 1.0): creative responses
# - Security: the model can generate unexpected content
# - Risk: higher probability of "breaking out" of restrictions
#   because it explores lower-probability tokens
# - Use: creative generation, brainstorming
# - Implication: guardrails must be stricter

creative_config = {
    "temperature": 0.9,
    "top_k": 100,
    "top_p": 0.95
}

# ZERO TEMPERATURE: deterministic response
# - Security: maximum reproducibility (ideal for auditing)
# - Risk: does not eliminate harmful content, only makes it predictable
# - Note: temperature 0 does not mean "safe" — it means
#   that if the most probable token is harmful, it always will be

audit_config = {
    "temperature": 0.0,
    "top_k": 1,  # Greedy decoding
    "top_p": 1.0
}
