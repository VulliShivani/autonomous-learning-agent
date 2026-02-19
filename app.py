import streamlit as st
from backend.db import create_tables
import requests
import pandas as pd

from llm import get_llm
from utils import generate_mcqs, evaluate_mcqs
from checkpoints import TOPICS
from backend.db import save_progress
from context import gather_context
from context_validator import validate_context
create_tables()
# ---------------- SAFE SESSION INIT ----------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "guest_user"
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
        "stage": "mode",          # mode | explain | explain_done | quiz | feynman | dashboard
        "topic": "",
        "checkpoint_idx": 0,
        "explanation": "",
        "feynman_explanation": "",
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

    with col1:
        st.markdown("### 🎯 Structured Mode")
        st.write("⭐ Organized curriculum with checkpoints")
        st.write("⭐ Progressive difficulty levels")
        st.write("⭐ Systematic skill building")

        if st.button("Start Structured Mode", use_container_width=True):
            st.session_state.mode = "Structured"
            st.session_state.stage = "explain"
            st.rerun()

    with col2:
        st.markdown("### 📘 Free Mode")
        st.write("⭐ Choose any topic you want")
        st.write("⭐ Flexible learning pace")
        st.write("⭐ Customized to your interests")

        if st.button("Start Free Mode", use_container_width=True):
            st.session_state.mode = "Free"
            st.session_state.stage = "explain"
            st.rerun()

    st.divider()

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
                f"Explain {st.session_state.topic} the information should be introduction,objectives,types, advantges,disadvantges for a beginner with examples."
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
            st.session_state.mcqs = generate_mcqs(llm,st.session_state.topic,num_questions=10)

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
                st.session_state["user_id"],
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
                f"Explain {st.session_state.topic} in very simple words. provide more examples to understand clearly .Give a small code example"
            ).content
        )

        if st.button("Retry Quiz"):
            st.session_state.attempt += 1
            st.session_state.mcqs = []
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()

# ================= STRUCTURED MODE =================
# ================= STRUCTURED MODE =================
if st.session_state.mode == "Structured":

    # ---------- Topic Selection ----------
    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = None

    if st.session_state.selected_topic is None:
        st.subheader("📚 Choose a Topic")

        topic_choice = st.selectbox(
            "Select Topic",
            list(TOPICS.keys())
        )

        if st.button("Start Topic"):
            st.session_state.selected_topic = topic_choice
            st.session_state.checkpoint_idx = 0
            st.session_state.stage = "explain"
            st.rerun()

        st.stop()

    # ---------- Load Checkpoints ----------
    CHECKPOINTS = TOPICS[st.session_state.selected_topic]
    topic = CHECKPOINTS[st.session_state.checkpoint_idx]

    # ---------- Progress Bar ----------
    st.progress(
        (st.session_state.checkpoint_idx + 1) / len(CHECKPOINTS)
    )

    st.caption(
        f"Checkpoint {st.session_state.checkpoint_idx + 1}/{len(CHECKPOINTS)}"
    )

    # ---------- Show All Checkpoints ----------
    st.markdown("### 📍 Checkpoints in this Topic")

    for idx, cp in enumerate(CHECKPOINTS):
        if idx == st.session_state.checkpoint_idx:
            st.write(f"➡️ **{cp}**")
        else:
            st.write(f"• {cp}")

    st.divider()

    # ---------- EXPLANATION ----------
    if st.session_state.stage == "explain":
        st.subheader(f"📖 {topic}")

        uploaded_file = st.file_uploader(
            "Upload your notes (optional)",
            type=["txt", "pdf"]
        )

        if st.button("Generate Explanation"):
            context = gather_context(topic, uploaded_file)
            relevance = validate_context(topic, context)

            st.info(f"📌 Context relevance score: {relevance}%")

            if relevance < 40:
                st.warning("Uploaded notes may not be relevant.")

            st.session_state.explanation = llm.invoke(
                f"""
Use this context to explain:

{context}

Explain clearly with examples.
"""
            ).content

            st.session_state.stage = "explain_done"
            st.rerun()

    # ---------- SHOW EXPLANATION ----------
    if st.session_state.stage == "explain_done":
        st.subheader("📖 Explanation")
        st.write(st.session_state.explanation)

        if st.button("Start Quiz"):
            st.session_state.mcqs = []
            st.session_state.attempt = 1
            st.session_state.stage = "quiz"
            st.rerun()

    # ---------- QUIZ ----------
    if st.session_state.stage == "quiz":
        st.subheader(f"📝 Quiz – Attempt {st.session_state.attempt}")

        if not st.session_state.mcqs:
            st.session_state.mcqs = generate_mcqs(
                llm,
                topic,
                num_questions=10   # 🔥 now 10 questions
            )

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

            score, feedback = evaluate_mcqs(
                st.session_state.mcqs,
                user_answers
            )

            st.session_state.score = score
            st.session_state.feedback = feedback

            save_progress(
                user_id=st.session_state["user_id"],
                mode="Structured",
                topic=topic,
                score=score,
                attempt=st.session_state.attempt
            )

            st.session_state.show_score = True
            st.rerun()

    # ---------- SCORE ----------
    if st.session_state.show_score:
        st.subheader(f"📊 Score: {st.session_state.score}%")

        for f in st.session_state.feedback:
            st.write(f)

        if st.session_state.score < 70:
            if st.button("Generate Feynman Explanation"):
                st.session_state.show_score = False
                st.session_state.stage = "feynman"
                st.rerun()
        else:
            if st.button("Next Checkpoint"):

                if st.session_state.checkpoint_idx + 1 < len(CHECKPOINTS):
                    st.session_state.checkpoint_idx += 1
                    st.session_state.stage = "explain"
                    st.session_state.show_score = False
                    st.rerun()
                else:
                    st.success("🎉 Topic Completed!")

    # ---------- FEYNMAN ----------
    if st.session_state.stage == "feynman":

        st.subheader("🔁 Feynman Explanation")

        if not st.session_state.feynman_explanation:
            st.session_state.feynman_explanation = llm.invoke(
                f"""
Explain {topic} in VERY simple words.
Give a small Python example.
Explain like teaching a child.
"""
            ).content

        st.write(st.session_state.feynman_explanation)

        if st.button("Retry Quiz"):
            st.session_state.attempt += 1
            st.session_state.mcqs = []
            st.session_state.feynman_explanation = ""
            st.session_state.show_score = False
            st.session_state.stage = "quiz"
            st.rerun()

# ================= DASHBOARD =================
if st.session_state.stage == "dashboard":
    st.subheader("📊 Learning Progress Dashboard")

    try:
        from backend.db import get_progress

        data = get_progress()

        if not data:
            st.info("No learning progress found yet.")
        else:
            df = pd.DataFrame(
                data,
                columns=["Mode", "Topic", "Score", "Attempt", "Timestamp"]
            )

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🕒 Recent Activity")
                st.dataframe(
                    df.sort_values("Timestamp", ascending=False).head(5)
                )

            with col2:
                st.markdown("### 📌 Summary")
                st.metric("Total Attempts", len(df))
                st.metric("Average Score", f"{df['Score'].mean():.1f}%")
                st.metric("Best Score", f"{df['Score'].max()}%")

            st.divider()

            st.markdown("### 📈 Score vs Attempt")
            attempt_df = df.groupby("Attempt", as_index=False)["Score"].mean()
            st.line_chart(
                attempt_df.set_index("Attempt"),
                use_container_width=True
            )

            st.markdown("### 📊 Average Score by Mode")
            st.bar_chart(
                df.groupby("Mode")["Score"].mean(),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Could not load progress: {e}")

    if st.button("⬅ Back to Home"):
        st.session_state.stage = "mode"
        st.rerun()
