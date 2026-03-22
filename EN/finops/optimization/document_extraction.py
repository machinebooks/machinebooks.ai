# Source: The FinOps Engineer and the Machine -- Chapter 9
# Pattern: Document field extraction with prompt caching

# Example: field extraction from a bid document
EXTRACTION_PROMPT_VERBOSE = """
Please analyze the following bid document text
and provide the most relevant fields you can identify,
including the title, base budget, deadline,
and whether economic solvency accreditation is required.

Document text:
{document_text}
"""
# Typical output tokens: ~180 tokens (explanatory text + data)

EXTRACTION_PROMPT_JSON = """Extract the indicated fields from the following text.
Respond ONLY with valid JSON, no additional text.

Expected schema:
{{
  "title": "string",
  "base_budget": number,
  "deadline": "YYYY-MM-DD",
  "requires_solvency": boolean
}}

Text:
{document_text}"""
# Typical output tokens: ~45 tokens (just the JSON)

def extract_fields(document_text: str, middleware: CachingMiddleware) -> dict:
    """
    Extracts structured fields with JSON mode.
    Output token reduction: ~75% compared to the verbose prompt.
    """
    import json

    response = middleware.create_with_cache(
        model="claude-haiku-4-5",  # extraction = FAST tier task
        system="You are a structured data extractor. Respond only with JSON.",
        user_message=EXTRACTION_PROMPT_JSON.format(document_text=document_text),
        max_tokens=256,  # limit adjusted to expected output
    )

    text = response.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: retry with a more explicit instruction
        # In production, log the failure for analysis
        return {}
