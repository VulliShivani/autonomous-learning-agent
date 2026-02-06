from typing import Optional
import io

def gather_context(topic: str, uploaded_file: Optional[io.BytesIO] = None) -> str:
    """
    Gathers learning context from:
    1. Topic / checkpoint
    2. Optional user-uploaded notes
    """

    context = f"Topic: {topic}\n"

    if uploaded_file is not None:
        try:
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")
            context += "\nUser Notes:\n" + file_text
        except Exception:
            context += "\nUser Notes: [Could not read uploaded file]"

    return context
