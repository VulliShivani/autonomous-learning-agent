import re

# Core Python / programming indicators
TECH_KEYWORDS = {
    "python", "code", "program", "variable", "function",
    "loop", "list", "tuple", "dictionary", "indentation",
    "syntax", "data", "type", "int", "float", "string"
}

def validate_context(topic: str, context: str) -> float:
    """
    Robust but lightweight relevance scoring (0–100)
    """

    if not context or len(context.strip()) < 30:
        return 0.0

    context = context.lower()
    topic = topic.lower()

    # ---- Step 1: Check for technical signals ----
    tech_hits = sum(1 for kw in TECH_KEYWORDS if kw in context)

    # If NO technical indicators → almost irrelevant
    if tech_hits == 0:
        return 5.0

    # ---- Step 2: Topic keyword matching ----
    topic_keywords = [
        w for w in re.findall(r"\w+", topic)
        if len(w) > 3
    ]

    topic_hits = sum(1 for kw in topic_keywords if kw in context)

    base_score = (topic_hits / max(len(topic_keywords), 1)) * 100

    # ---- Step 3: Confidence scaling ----
    relevance = (base_score * 0.7) + (min(tech_hits, 5) * 6)

    # ---- Step 4: Length sanity check ----
    if len(context.split()) < 50:
        relevance *= 0.6

    return round(min(relevance, 100), 2)
