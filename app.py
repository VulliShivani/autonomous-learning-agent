import streamlit as st
from llm import get_llm
from utils import generate_mcqs, evaluate_mcqs
from checkpoints import CHECKPOINTS

# ---------------- PAGE SETUP ----------------
st.set_page_config("Autonomous Learning Agent", layout="wide")
st.title("🧠 Autonomous Learning Agent")

llm = get_llm()

# ---------------- SESSION STATE ----------------
def init_state():
    defaults = {
        "mode": None,
        "stage": "mode",   # mode | explain | explain_done | quiz | feynman | done
        "topic": "",
        "checkpoint_idx": 0,
        "explanation": "",
        "mcqs": [],
        "attempt": 1,
        "show_score": False,
        "score": 0,
        "feedback": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- TOP BACK BUTTON ----------------
if st.button("⬅ Back to Mode Selection"):
    st.session_state.stage = "mode"
    st.session_state.mode = None
    st.session_state.mcqs = []
    st.session_state.show_score = False
    st.rerun()

st.divider()

# ================= MODE SELECTION =================
if st.session_state.stage == "mode":
    st.markdown("## Adaptive Learning Platform")
    st.caption("Choose your learning mode to begin your journey")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Structured Mode")
        st.write("Follow a checkpoint-based learning path with guided progression through topics")
        st.write("⭐Organized curriculum with checkpoints")
        st.write("⭐Progressive difficulty levels")
        st.write("⭐Systematic skill building")
        if st.button("Start Structured Mode"):
            st.session_state.mode = "Structured Mode"
            st.session_state.stage = "explain"
            st.rerun()

    with col2:
        st.markdown("### 📘 Free Mode")
        st.write("Learn any topic of your choice withpersonalized adaptive content")
        st.write("⭐Choose any topic you want")
        st.write("⭐Flexible learning pace")
        st.write("⭐Customized to your intrests")

        if st.button("Start Free Mode"):
            st.session_state.mode = "Free Mode"
            st.session_state.stage = "explain"
            st.rerun()

# ================= FREE MODE =================
if st.session_state.mode == "Free Mode":

    # -------- Explanation --------
    if st.session_state.stage == "explain":
        st.subheader("📘 Free Mode")
        st.session_state.topic = st.text_input("Enter Topic")

        if st.button("Generate Explanation"):
            st.session_state.explanation = llm.invoke(
                f"Explain {st.session_state.topic} for a beginner with examples."
            ).content
            st.session_state.stage = "explain_done"
            st.rerun()

    # -------- Show Explanation + Start Quiz --------
    if st.session_state.stage == "explain_done":
        st.subheader("📖 Explanation")
        st.write(st.session_state.explanation)

        if st.button("Start Quiz"):
            st.session_state.mcqs = []
            st.session_state.attempt = 1
            st.session_state.stage = "quiz"
            st.rerun()

    # -------- Quiz --------
    if st.session_state.stage == "quiz":
        st.subheader(f"📝 Quiz – Attempt {st.session_state.attempt}")

        if not st.session_state.mcqs:
            st.session_state.mcqs = generate_mcqs(llm, st.session_state.topic)

        user_answers = []
        for i, q in enumerate(st.session_state.mcqs):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            ans = st.radio(
                "Choose an option",
                [f"{k}) {v}" for k, v in q["options"].items()],
                key=f"free_{st.session_state.attempt}_{i}"
            )
            user_answers.append(ans[0])

        if st.button("Submit Quiz"):
            score, feedback = evaluate_mcqs(st.session_state.mcqs, user_answers)
            st.session_state.score = score
            st.session_state.feedback = feedback
            st.session_state.show_score = True
            st.rerun()

    # -------- Score --------
    if st.session_state.show_score:
        st.subheader(f"📊 Score: {st.session_state.score}%")
        for f in st.session_state.feedback:
            st.write(f)

        if st.session_state.score < 70:
            if st.button("Generate Feynman Explanation"):
                st.session_state.stage = "feynman"

        else:
            if st.button("Finish"):
                st.session_state.clear()
                st.rerun()

    # -------- Feynman Explanation --------
    if st.session_state.stage == "feynman":
        st.subheader("🔁 Feynman Explanation")
        st.write(
            llm.invoke(
                f"Explain {st.session_state.topic} in very simple words like to a child."
            ).content
        )

        if st.button("Retry Quiz"):
            st.session_state.mcqs = []
            st.session_state.attempt += 1
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()

# ================= STRUCTURED MODE =================
if st.session_state.mode == "Structured Mode":

    topic = CHECKPOINTS[st.session_state.checkpoint_idx]

    st.progress(st.session_state.checkpoint_idx / len(CHECKPOINTS))
    st.caption(f"Checkpoint {st.session_state.checkpoint_idx + 1}/{len(CHECKPOINTS)}")

    if st.session_state.stage == "explain":
        st.subheader(f"📍 {topic}")

        if st.button("Generate Explanation"):
            st.session_state.explanation = llm.invoke(
                f"Explain {topic} for a beginner with examples."
            ).content
            st.session_state.stage = "explain_done"
            st.rerun()

    if st.session_state.stage == "explain_done":
        st.subheader("📖 Explanation")
        st.write(st.session_state.explanation)

        if st.button("Start Quiz"):
            st.session_state.mcqs = []
            st.session_state.attempt = 1
            st.session_state.stage = "quiz"
            st.rerun()

    if st.session_state.stage == "quiz":
        st.subheader(f"📝 Quiz – Attempt {st.session_state.attempt}")

        if not st.session_state.mcqs:
            st.session_state.mcqs = generate_mcqs(llm, topic)

        user_answers = []
        for i, q in enumerate(st.session_state.mcqs):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            ans = st.radio(
                "Choose an option",
                [f"{k}) {v}" for k, v in q["options"].items()],
                key=f"struct_{st.session_state.attempt}_{i}"
            )
            user_answers.append(ans[0])

        if st.button("Submit Quiz"):
            score, feedback = evaluate_mcqs(st.session_state.mcqs, user_answers)
            st.session_state.score = score
            st.session_state.feedback = feedback
            st.session_state.show_score = True
            st.rerun()

    if st.session_state.show_score:
        st.subheader(f"📊 Score: {st.session_state.score}%")
        for f in st.session_state.feedback:
            st.write(f)

        if st.session_state.score < 70:
            if st.button("Generate Feynman Explanation"):
                st.session_state.stage = "feynman"
        else:
            if st.button("Next Checkpoint"):
                st.session_state.checkpoint_idx += 1
                st.session_state.stage = "explain"
                st.session_state.show_score = False
                st.rerun()

    if st.session_state.stage == "feynman":
        st.subheader("🔁 Feynman Explanation")
        st.write(
            llm.invoke(
                f"Explain {topic} in very simple words like to a child."
            ).content
        )

        if st.button("Retry Quiz"):
            st.session_state.mcqs = []
            st.session_state.attempt += 1
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()
