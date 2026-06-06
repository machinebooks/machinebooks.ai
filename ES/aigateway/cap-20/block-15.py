# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/output_filter_service.py:137-168

# Check if actual system prompt text appears in output
if system_prompt and len(system_prompt) > 50:
    prompt_lower = system_prompt.lower()
    content_lower = content.lower()
    window_size = min(100, len(prompt_lower) // 2)

    if window_size > 20:
        for i in range(0, len(prompt_lower) - window_size, 50):
            fragment = prompt_lower[i:i + window_size]
            if fragment in content_lower:
                result.flags.append("system_prompt_content_leak")
                result.risk_score += 50
                # Redactar el fragmento del system prompt del output
                idx = content_lower.find(fragment)
                if idx >= 0:
                    result.filtered_content = (
                        result.filtered_content[:idx]
                        + "[REDACTED - system prompt]"
                        + result.filtered_content[idx + window_size:]
                    )
                break
