import streamlit as st
import requests
import pandas as pd

from llm import get_llm
from utils import generate_mcqs, evaluate_mcqs
from checkpoints import CHECKPOINTS
from backend.db import save_progress

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Autonomous Learning Agent",
    layout="wide"
)
st.title("🧠 Autonomous Learning Agent")

llm = get_llm()

# ---------------- SESSION STATE ----------------
def init_state():
    defaults = {
        "mode": None,
        "stage": "mode",   # mode | explain | explain_done | quiz | feynman | dashboard
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

# ---------------- BACK BUTTON ----------------
if st.button("⬅ Back to Mode Selection"):
    st.session_state.clear()
    init_state()
    st.rerun()

st.divider()

# ================= MODE SELECTION =================
if st.session_state.stage == "mode":
    st.markdown("## Adaptive Learning Platform")
    st.caption("Choose how you want to learn")

    col1, col2 = st.columns(2, gap="large")

    # -------- STRUCTURED MODE CARD --------
    with col1:
        st.markdown("### 🎯 Structured Mode")
        st.write("⭐ Organized curriculum with checkpoints")
        st.write("⭐ Progressive difficulty levels")
        st.write("⭐ Systematic skill building")

        st.markdown("")  # spacing

        if st.button("Start Structured Mode", use_container_width=True):
            st.session_state.mode = "Structured"
            st.session_state.stage = "explain"
            st.rerun()

    # -------- FREE MODE CARD --------
    with col2:
        st.markdown("### 📘 Free Mode")
        st.write("⭐ Choose any topic you want")
        st.write("⭐ Flexible learning pace")
        st.write("⭐ Customized to your interests")

        st.markdown("")  # spacing

        if st.button("Start Free Mode", use_container_width=True):
            st.session_state.mode = "Free"
            st.session_state.stage = "explain"
            st.rerun()

    st.divider()

    # -------- VIEW PROGRESS BUTTON --------
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        if st.button("📊 View Learning Progress", use_container_width=True):
            st.session_state.stage = "dashboard"
            st.rerun()

# ================= FREE MODE =================
if st.session_state.mode == "Free":

    if st.session_state.stage == "explain":
        st.subheader("📘 Free Mode")
        st.session_state.topic = st.text_input("Enter a topic")

        if st.button("Generate Explanation"):
            st.session_state.explanation = llm.invoke(
                f"Explain {st.session_state.topic} for a beginner with examples."
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

            save_progress(
                mode="Free",
                topic=st.session_state.topic,
                score=score,
                attempt=st.session_state.attempt
            )

            st.session_state.show_score = True
            st.rerun()

    if st.session_state.show_score:
        st.subheader(f"📊 Score: {st.session_state.score}%")

        for f in st.session_state.feedback:
            st.write(f)

        if st.session_state.score < 70:
            if st.button("Generate Feynman Explanation"):
                st.session_state.stage = "feynman"
                st.rerun()
        else:
            if st.button("Finish"):
                st.session_state.clear()
                init_state()
                st.rerun()

    if st.session_state.stage == "feynman":
        st.subheader("🔁 Feynman Explanation")
        st.write(
            llm.invoke(
                f"Explain {st.session_state.topic} in very simple words like to a child."
            ).content
        )

        if st.button("Retry Quiz"):
            st.session_state.attempt += 1
            st.session_state.mcqs = []
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()

# ================= STRUCTURED MODE =================
if st.session_state.mode == "Structured":

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

            save_progress(
                mode="Structured",
                topic=topic,
                score=score,
                attempt=st.session_state.attempt
            )

            st.session_state.show_score = True
            st.rerun()

    if st.session_state.show_score:
        st.subheader(f"📊 Score: {st.session_state.score}%")

        for f in st.session_state.feedback:
            st.write(f)

        if st.session_state.score < 70:
            if st.button("Generate Feynman Explanation"):
                st.session_state.stage = "feynman"
                st.rerun()
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
            st.session_state.attempt += 1
            st.session_state.mcqs = []
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()

# ================= DASHBOARD =================
if st.session_state.stage == "dashboard":
    st.subheader("📊 Learning Progress Dashboard")

    try:
        response = requests.get("http://127.0.0.1:8000/progress")
        data = response.json()

        if not data:
            st.info("No learning progress found yet.")
        else:
            df = pd.DataFrame(
                data,
                columns=["Mode", "Topic", "Score", "Attempt", "Timestamp"]
            )
            st.markdown("### 📋 Attempt History")
            st.dataframe(df)

            
            # Convert timestamp
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            df = df.sort_values("Timestamp", ascending=False)

            # ---------- LAYOUT ----------
            col1, col2 = st.columns([2, 1])

            # ---------- RECENT ACTIVITY ----------
            with col1:
                st.markdown("### 🕒 Recent Activity")
                recent_df = df.head(5)[
                    ["Mode", "Topic", "Score", "Attempt", "Timestamp"]
                ]
                st.dataframe(
                    recent_df,
                    use_container_width=True
                )

            # ---------- SUMMARY STATS ----------
            with col2:
                st.markdown("### 📌 Summary")
                st.metric("Total Attempts", len(df))
                st.metric("Average Score", f"{df['Score'].mean():.1f}%")
                st.metric("Best Score", f"{df['Score'].max()}%")

            st.divider()

            # ---------- SCORE vs ATTEMPT ----------
            st.markdown("### 📈 Score vs Attempt")

            attempt_df = (
                df.groupby("Attempt", as_index=False)["Score"]
                .mean()
                .sort_values("Attempt")
            )

            st.line_chart(
                attempt_df.set_index("Attempt"),
                use_container_width=True
            )

            st.divider()

            # ---------- MODE COMPARISON ----------
            st.markdown("### 📊 Average Score by Mode")
            avg_scores = df.groupby("Mode")["Score"].mean()
            st.bar_chart(avg_scores, use_container_width=True)

    except Exception as e:
        st.error(f"Could not load progress: {e}")

    if st.button("⬅ Back to Home"):
        st.session_state.stage = "mode"
        st.rerun()
