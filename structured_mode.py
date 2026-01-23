# structured_mode.py

from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel
from checkpoints import CHECKPOINTS
from state import LearnerState, start_checkpoint, gather_context


def explain_topic(state: LearnerState, llm: BaseChatModel) -> LearnerState:
    topic = CHECKPOINTS[state.current_checkpoint_index]

    print(f"\n===== CHECKPOINT {state.current_checkpoint_index + 1} =====")
    print(f"Topic: {topic}")

    response = llm.invoke(
        f"Explain {topic} for a beginner with example and code."
    )

    state.explanation = response.content
    print("\n[AI Explanation]\n", response.content)
    return state


def generate_mcqs(state: LearnerState, llm):
    topic = CHECKPOINTS[state.current_checkpoint_index]

    raw = llm.invoke(
        f"""
Create 3 beginner MCQs on {topic}.

Format EXACTLY like this:

Q1. Question?
A) option
B) option
C) option
D) option
Answer: B
"""
    ).content

    questions = []
    answers = []

    for block in raw.split("\n\n"):
        lines = block.split("\n")
        q = []
        ans = None
        for line in lines:
            if line.startswith("Answer:"):
                ans = line.split(":")[1].strip().upper()
            else:
                q.append(line)
        if ans:
            questions.append(q)
            answers.append(ans)

    correct = 0
    print("\n--- QUIZ ---\n")

    for i, q in enumerate(questions):
        for line in q:
            print(line)
        user_ans = input("Your answer (A/B/C/D): ").strip().upper()
        if user_ans == answers[i]:
            print("✅ Correct\n")
            correct += 1
        else:
            print(f"❌ Wrong (Correct: {answers[i]})\n")

    state.score = (correct / len(answers)) * 100
    print(f"Your Score: {state.score}%")
    return state


def explain_simpler(state: LearnerState, llm):
    topic = CHECKPOINTS[state.current_checkpoint_index]

    response = llm.invoke(
        f"""
Explain {topic} using VERY SIMPLE words.
expalin with the help of codes
Use short sentences and a small example.
Explain like teaching a 10-year-old.
"""
    )

    print("\n🔁 SIMPLER EXPLANATION (Feynman Technique)\n")
    print(response.content)
    state.explanation = response.content
    return state


def advance_checkpoint(state: LearnerState) -> LearnerState:
    state.current_checkpoint_index += 1
    state.explanation = None
    state.score = 0.0
    return state


def result_router(state: LearnerState):
    if state.score >= 70:
        if state.current_checkpoint_index + 1 >= len(CHECKPOINTS):
            return END
        return "advance"
    return "simpler"


def run_structured_mode(llm: BaseChatModel):
    graph = StateGraph(LearnerState)

    graph.add_node("start", start_checkpoint)
    graph.add_node("gather", gather_context)
    graph.add_node("explain", lambda s: explain_topic(s, llm))
    graph.add_node("mcq", lambda s: generate_mcqs(s, llm))
    graph.add_node("simpler", lambda s: explain_simpler(s, llm))
    graph.add_node("advance", advance_checkpoint)

    graph.set_entry_point("start")

    graph.add_edge("start", "gather")
    graph.add_edge("gather", "explain")
    graph.add_edge("explain", "mcq")
    graph.add_edge("advance", "gather")
    graph.add_edge("simpler", "mcq")

    graph.add_conditional_edges(
        "mcq",
        result_router,
        {
            "advance": "advance",
            "simpler": "simpler",
            END: END
        }
    )

    graph.compile().invoke(LearnerState())
