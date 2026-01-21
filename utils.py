import json

def generate_mcqs(llm, topic):
    prompt = f"""
Generate exactly 3 MCQs on {topic}.
Return ONLY valid JSON.

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
    "explanation": "Explanation"
  }}
]
"""
    raw = llm.invoke(prompt).content
    raw = raw[raw.find("["):raw.rfind("]")+1]
    return json.loads(raw)

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

    score = (correct / len(mcqs)) * 100
    return score, feedback
