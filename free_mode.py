from utils import generate_mcqs, evaluate_mcqs


# free_mode.py

def run_free_mode(llm, topic: str):
    explanation = llm.invoke(
        f"""
Explain {topic} for a beginner.
Include simple explanation, example, and real-life use.
"""
    ).content

    print("\n[Explanation]\n")
    print(explanation)