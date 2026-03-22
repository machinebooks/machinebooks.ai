# Companion code for "The Cyber Range and the Machine" — Chapter 18
# AI coaching service: reactive hints, stall detection, flag leak prevention.
# This is STARTER code — not production-ready.
#
# Requires: pip install anthropic

import os
import re
import time

import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "<YOUR_API_KEY>")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
FLAG_PREFIX = os.getenv("FLAG_PREFIX", "CYBERRANGE")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# -- Flag leak prevention (Chapter 18: critical guardrail) -----------------

FLAG_PATTERN = re.compile(
    r"(?:CYBERRANGE|FLAG|CTF)\{[a-fA-F0-9]+\}",
    re.IGNORECASE,
)


def sanitize_output(text: str) -> str:
    """
    Remove any flag-like patterns from AI output.

    Chapter 18 explains why this is essential:
    - The AI coach has access to challenge context including flag hashes
    - We must NEVER leak actual flags in hints
    - This is a defense-in-depth measure alongside prompt engineering
    """
    return FLAG_PATTERN.sub("[FLAG_REDACTED]", text)


# -- Stall detection (Chapter 18: know when the player is stuck) -----------

STALL_THRESHOLD_SECONDS = 600  # 10 minutes without meaningful progress


def detect_stall(
    last_activity_timestamp: float,
    hints_given: int,
    max_hints: int = 5,
) -> dict:
    """
    Determine if a player is stalled and what level of hint to offer.

    Chapter 18 covers the progressive hint ladder:
    - Level 0: General encouragement ("Have you tried enumerating services?")
    - Level 1: Direction hint ("Look at the web server on port 8080")
    - Level 2: Technique hint ("This vulnerability involves SQL injection")
    - Level 3: Specific guidance ("Try the login form with ' OR 1=1--")
    - Level 4: Walkthrough reference ("See this resource for the technique")
    """
    elapsed = time.time() - last_activity_timestamp
    is_stalled = elapsed > STALL_THRESHOLD_SECONDS

    if not is_stalled:
        return {"stalled": False, "hint_level": 0}

    # Progressive hint level based on how many hints already given
    hint_level = min(hints_given + 1, 4)

    return {
        "stalled": True,
        "idle_seconds": int(elapsed),
        "hint_level": hint_level,
        "hints_remaining": max(0, max_hints - hints_given),
    }


# -- Hint generation (Chapter 18: context-aware coaching) ------------------

HINT_LEVEL_INSTRUCTIONS = {
    0: "Give only vague encouragement. Do NOT mention specific tools or techniques.",
    1: "Point the player toward the right area (e.g., a specific service or port) but do NOT reveal the vulnerability type.",
    2: "Name the vulnerability category (e.g., 'SQL injection') but do NOT give exploitation steps.",
    3: "Provide a specific technique or command to try, but do NOT give the exact payload.",
    4: "Give a near-complete walkthrough with a reference link, but NEVER reveal the flag.",
}


def generate_hint(
    challenge_description: str,
    player_actions: list[str],
    hint_level: int = 1,
) -> str:
    """
    Generate a context-aware hint for a stuck player.

    Args:
        challenge_description: What the challenge is about (no flag values!)
        player_actions: List of recent player actions/commands
        hint_level: 0-4, controls how specific the hint is

    Returns:
        Sanitized hint string (flag patterns removed).
    """
    level_instruction = HINT_LEVEL_INSTRUCTIONS.get(hint_level, HINT_LEVEL_INSTRUCTIONS[1])
    recent_actions = "\n".join(player_actions[-10:]) if player_actions else "No actions recorded."

    system_prompt = (
        "You are a cybersecurity training coach in a Cyber Range. "
        "Help the player progress without giving away the answer.\n\n"
        "CRITICAL RULES:\n"
        "- NEVER reveal flag values, even partially\n"
        "- NEVER provide the exact exploit payload that solves the challenge\n"
        "- Encourage the learning process over speed\n"
        "- Reference real-world tools and techniques\n\n"
        f"HINT LEVEL: {hint_level}/4\n"
        f"INSTRUCTION: {level_instruction}"
    )

    user_message = (
        f"Challenge: {challenge_description}\n\n"
        f"Player's recent actions:\n{recent_actions}\n\n"
        "Generate an appropriate hint."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_hint = response.content[0].text

    # Defense-in-depth: sanitize even though the prompt says not to leak flags
    return sanitize_output(raw_hint)


# -- Session management helpers --------------------------------------------

def should_offer_hint(
    last_activity: float,
    hints_given: int,
    max_hints: int = 5,
    player_requested: bool = False,
) -> bool:
    """
    Decide whether to proactively offer a hint.

    Chapter 18: we offer hints in two modes:
    - Reactive: player explicitly asks for help
    - Proactive: system detects stall and nudges the player
    """
    if player_requested and hints_given < max_hints:
        return True

    stall_info = detect_stall(last_activity, hints_given, max_hints)
    return stall_info["stalled"] and stall_info["hints_remaining"] > 0
