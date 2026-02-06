from typing import Optional
import io

def run_free_mode(
    llm,
    topic: str,
    user_notes: Optional[str] = None
):
    """
    Free mode explanation with optional context from user notes
    """

    # -------- Context Gathering --------
    context = f"Topic: {topic}\n"

    if user_notes:
        context += f"\nUser Notes:\n{user_notes}"

    # -------- LLM Explanation --------
    explanation = llm.invoke(
        f"""
You are an intelligent learning assistant.

Use the following context to explain the topic clearly:

{context}

Explain the topic in simple terms.
Include:
- Simple explanation
- One example
- One real-life use case
"""
    ).content

    return explanation
