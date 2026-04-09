# Extracted from: LibroAISafety/ch-03-inside-the-model.md
# Logprobs analysis to detect information leakage
# Didactic example with a provider API that exposes logprobs

def analyze_uncertainty(response) -> dict:
    """Analyzes token probabilities to detect
    patterns indicating the model 'knows' something
    it is trying not to say."""
    tokens_analysis = []

    for token_info in response.logprobs:
        prob_chosen = token_info["probability"]
        # If the chosen token has low probability,
        # the model was "hesitating" — possible signal of
        # conflict between knowledge and restrictions
        if prob_chosen < 0.3:
            # Examine the discarded alternatives
            alternatives = token_info.get("top_alternatives", [])
            tokens_analysis.append({
                "token": token_info["token"],
                "prob": prob_chosen,
                "alternatives": alternatives,
                # High entropy + active restriction =
                # the model knows the answer but is trying not to give it
                "possible_suppression": len(alternatives) > 5
                    and prob_chosen < 0.15
            })

    return {
        "tokens_analyzed": len(tokens_analysis),
        "possible_suppressions": sum(
            1 for t in tokens_analysis if t["possible_suppression"]
        )
    }
