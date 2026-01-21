from utils import generate_mcqs, evaluate_mcqs


def run_free_mode(llm, topic: str, st):
    """
    Free Mode with:
    - Explanation
    - Quiz
    - Evaluation
    - Feynman re-explanation if score < 70
    - Quiz again (loop)
    """

    # ---------- INITIALIZE SESSION STATE ----------
    if "attempt" not in st.session_state:
        st.session_state.attempt = 1

    if "phase" not in st.session_state:
        st.session_state.phase = "explain"

    # ---------- EXPLANATION PHASE ----------
    if st.session_state.phase == "explain":
        explanation = llm.invoke(
            f"""
Explain {topic} for a beginner.
Include:
- Simple explanation
- Example
- Real-world use cases
"""
        ).content

        st.subheader("📘 Explanation")
        st.write(explanation)

        st.session_state.mcqs = generate_mcqs(llm, topic)
        st.session_state.phase = "quiz"

    # ---------- QUIZ PHASE ----------
    if st.session_state.phase == "quiz":
        st.subheader(f"📝 Quiz (Attempt {st.session_state.attempt})")

        user_answers = []

        for i, q in enumerate(st.session_state.mcqs):
            st.write(f"**Q{i+1}. {q['question']}**")

            options = [f"{k}) {v}" for k, v in q["options"].items()]
            selected = st.radio(
                f"Choose answer for Q{i+1}",
                options,
                key=f"q_{st.session_state.attempt}_{i}"
            )

            user_answers.append(selected[0])  # A/B/C/D

        if st.button("Submit Quiz"):
            score, feedback = evaluate_mcqs(
                st.session_state.mcqs, user_answers
            )

            st.write(f"### 📊 Score: {score}%")

            for fb in feedback:
                st.write(fb)

            # ---------- IF PASSED ----------
            if score >= 70:
                st.success("🎉 Great job! You understood the topic.")
                st.session_state.phase = "done"

            # ---------- IF FAILED → FEYNMAN ----------
            else:
                st.warning(
                    "Score < 70%. Re-explaining using Feynman Technique."
                )
                st.session_state.phase = "feynman"

    # ---------- FEYNMAN EXPLANATION ----------
    if st.session_state.phase == "feynman":
        simpler = llm.invoke(
            f"""
Explain {topic} again using the Feynman Technique.

Rules:
- Very simple words
- Short sentences
- Real-life analogy
- Practical use cases
- Small example
Explain as if teaching a 10-year-old.
"""
        ).content

        st.subheader("🔁 Feynman Explanation")
        st.write(simpler)

        # 🔁 Generate NEW quiz again
        st.session_state.mcqs = generate_mcqs(llm, topic)
        st.session_state.attempt += 1
        st.session_state.phase = "quiz"

        st.info("Try the quiz again below 👇")

    # ---------- DONE ----------
    if st.session_state.phase == "done":
        st.success("✅ Learning completed successfully!")
