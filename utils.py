import json


def generate_mcqs(llm, topic, num_questions=10):
    prompt = f"""
Generate exactly {num_questions} multiple choice questions on {topic}.

Return ONLY valid JSON in this format:

[
  {{
    "question": "...",
    "options": {{
      "A": "...",
      "B": "...",
      "C": "...",
      "D": "..."
    }},
    "answer": "A",
    "explanation": "Short explanation why correct"
  }}
]

Do not include any extra text.
Only return JSON.
"""

    raw = llm.invoke(prompt).content

    # Extract JSON safely
    try:
        raw = raw[raw.find("["):raw.rfind("]") + 1]
        return json.loads(raw)
    except Exception:
        # fallback if model gives messy output
        return []


def evaluate_mcqs(mcqs, user_answers):
    correct = 0
    feedback = []

    for i, q in enumerate(mcqs):
        if user_answers[i] == q["answer"]:
            correct += 1
            feedback.append(f"✅ Q{i+1} Correct")
        else:
            feedback.append(
                f"❌ Q{i+1} Wrong | Correct: {q['answer']} – {q['explanation']}"
            )

    score = round((correct / len(mcqs)) * 100, 2)

    return score, feedback
