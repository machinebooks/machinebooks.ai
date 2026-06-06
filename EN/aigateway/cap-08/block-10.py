# Extracted from: LibroAIGateway/cap-08-caching.md
# gateway/app/services/semantic_cache_service.py:4-7 (docstring)
"""
Designed for safe purposes (chat, quick_qa, translate, summarize) where
a question with similar wording can legitimately share an answer.
Do NOT enable on orchestrators (document, evaluate, proposal): cross-poisoning between
similar sections can return wrong answers.
"""
