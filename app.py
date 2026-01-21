import streamlit as st
from llm import get_llm
from utils import generate_mcqs, evaluate_mcqs
from checkpoints import CHECKPOINTS

def navigation_bar():
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏠 Home"):
            st.session_state.clear()
            st.session_state.stage = "mode"
            st.rerun()

    with col2:
        if st.button("🔁 Restart Current Mode"):
            mode = st.session_state.get("mode")
            st.session_state.clear()
            st.session_state.mode = mode
            st.session_state.stage = "explain"
            st.rerun()

    with col3:
        if st.button("❌ Reset Everything"):
            st.session_state.clear()
            st.rerun()

# ---------------- PAGE CONFIG ----------------
st.set_page_config("Autonomous Learning Agent", layout="wide")
st.title("🧠 Autonomous Learning Agent")
st.markdown(
    """
    <style>
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

navigation_bar()
st.divider()

llm = get_llm()

# ---------------- SESSION STATE INIT ----------------
def init_state():
    defaults = {
        "mode": None,
        "stage": "mode",
        "topic": "",
        "checkpoint_idx": 0,
        "mcqs": [],
        "attempt": 1,
        "score": None,
        "show_retry": False,
        "show_next": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def reset_all():
    st.session_state.clear()
    st.rerun()

# ================= MODE SELECTION =================
if st.session_state.stage == "mode":
    st.subheader("Choose Learning Mode")

    st.session_state.mode = st.radio(
        "Select learning mode",
        ["Structured Mode", "Free Mode"],
        label_visibility="collapsed"
    )

    if st.button("Start Learning"):
        st.session_state.stage = "explain"
        st.rerun()

# ================= FREE MODE =================
if st.session_state.mode == "Free Mode":

    # -------- EXPLANATION --------
    if st.session_state.stage == "explain":
        st.subheader("📘 Free (On Demand) Mode")

        st.session_state.topic = st.text_input("Enter Topic")

        if st.button("Start Learning"):
            explanation = llm.invoke(
                f"""
Explain {st.session_state.topic} in VERY DETAIL.
Include:
- definition
- importance
- step-by-step explanation
- examples
- real-life analogy
Explain for a beginner.
"""
            ).content

            # ✅ store explanation so it doesn't disappear
            st.session_state.free_explanation = explanation
            st.session_state.stage = "explained"
            st.rerun()

    # -------- SHOW EXPLANATION (STAYS VISIBLE) --------
    if st.session_state.stage == "explained":
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("📖 Explanation")
        st.write(st.session_state.free_explanation)

        st.markdown('</div>', unsafe_allow_html=True)


        # ✅ quiz starts ONLY when user clicks
        if st.button("Start Quiz"):
            st.session_state.mcqs = generate_mcqs(
                llm, st.session_state.topic
            )
            st.session_state.attempt = 1
            st.session_state.stage = "quiz"
            st.rerun()

    # -------- QUIZ --------
    if st.session_state.stage == "quiz":
        st.subheader(f"📝 Quiz – Attempt {st.session_state.attempt}")

        user_answers = []

        for i, q in enumerate(st.session_state.mcqs):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            ans = st.radio(
                f"Answer {i+1}",
                [f"{k}) {v}" for k, v in q["options"].items()],
                label_visibility="collapsed",
                key=f"free_{st.session_state.attempt}_{i}"
            )
            user_answers.append(ans[0])
        
        if st.button("Submit Quiz"):
            score, feedback = evaluate_mcqs(
                st.session_state.mcqs, user_answers
            )

            st.subheader(f"Score: {score:.2f}%")
            for f in feedback:
                st.write(f)

            if score < 70:
                st.warning("Applying Feynman Explanation")

                feynman = llm.invoke(
                    f"""
Explain {st.session_state.topic} again
using very simple words,
step-by-step,
like teaching a child.
"""
                ).content

                # show feynman explanation clearly
                st.subheader("🔁 Simpler Explanation")
                st.write(feynman)

                if st.button("Retry Quiz"):
                    st.session_state.mcqs = generate_mcqs(
                        llm, st.session_state.topic
                    )
                    st.session_state.attempt += 1
                    st.session_state.stage = "quiz"
                    st.rerun()

            else:
                st.success("🎉 You have mastered this topic!")
                if st.button("Finish"):
                    st.session_state.clear()
                    st.rerun()

# ================= STRUCTURED MODE =================
if st.session_state.mode == "Structured Mode":

    if st.session_state.checkpoint_idx >= len(CHECKPOINTS):
        st.success("🎓 All checkpoints completed!")
        st.button("Restart Learning", on_click=reset_all)

    else:
        checkpoint_topic = CHECKPOINTS[st.session_state.checkpoint_idx]

        # -------- EXPLANATION --------
        if st.session_state.stage == "explain":
            st.subheader(
                f"Checkpoint {st.session_state.checkpoint_idx + 1}: {checkpoint_topic}"
            )

            explanation = llm.invoke(
                f"""
Explain {checkpoint_topic} in VERY DETAIL.
Include:
- definition
- importance
- step-by-step explanation
- examples
- real-life analogy
Explain for a beginner.
"""
            ).content

            st.write(explanation)

            if st.button("Start Quiz"):
                st.session_state.mcqs = generate_mcqs(llm, checkpoint_topic)
                st.session_state.stage = "quiz"
                st.session_state.attempt = 1
                st.session_state.show_retry = False
                st.session_state.show_next = False
                st.rerun()

        # -------- QUIZ --------
        if st.session_state.stage == "quiz":
            st.subheader(
                f"📝 Quiz – Attempt {st.session_state.attempt}"
            )

            user_answers = []

            for i, q in enumerate(st.session_state.mcqs):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                ans = st.radio(
                    f"Answer {i+1}",
                    [f"{k}) {v}" for k, v in q["options"].items()],
                    label_visibility="collapsed",
                    key=f"struct_{st.session_state.attempt}_{i}"
                )
                user_answers.append(ans[0])

            if st.button("Submit Quiz"):
                score, feedback = evaluate_mcqs(
                    st.session_state.mcqs, user_answers
                )

                st.subheader(f"Score: {score:.2f}%")
                for f in feedback:
                    st.write(f)

                if score < 70:
                    st.warning("Score < 70% → Feynman Explanation")

                    feynman = llm.invoke(
                        f"""
Explain {checkpoint_topic} again
using very simple words,
step-by-step,
like teaching a child.
"""
                    ).content

                    st.write(feynman)
                    st.session_state.show_retry = True

                else:
                    st.success("✅ Checkpoint Passed")
                    st.session_state.show_next = True

        # -------- RETRY QUIZ --------
        if st.session_state.show_retry:
            if st.button("Retry Quiz"):
                st.session_state.mcqs = generate_mcqs(llm, checkpoint_topic)
                st.session_state.attempt += 1
                st.session_state.stage = "quiz"
                st.session_state.show_retry = False
                st.rerun()

        # -------- NEXT CHECKPOINT --------
        if st.session_state.show_next:
            if st.button("Next Checkpoint"):
                st.session_state.checkpoint_idx += 1
                st.session_state.stage = "explain"
                st.session_state.attempt = 1
                st.session_state.mcqs = []
                st.session_state.show_next = False
                st.rerun()