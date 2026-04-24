import streamlit as st
import json
import os
import random

def load_week(week):
    path = f"data/week{week}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def load_all():
    all_q = []
    for i in range(13):
        all_q.extend(load_week(i))
    return all_q

st.set_page_config(page_title="NPTEL Quiz", layout="centered")

st.title("NPTEL Quiz Portal")

ui_mode = st.radio("Interface", ["Desktop", "Mobile"])
mode = st.radio("Mode", ["Single Week", "All Weeks Combined"])

if mode == "Single Week":
    week = st.selectbox("Select Week", list(range(13)))
    questions = load_week(week)
else:
    questions = load_all()

shuffle_q = st.checkbox("Shuffle Questions")
shuffle_opt = st.checkbox("Shuffle Options")

# SESSION STATES
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# START QUIZ
if not st.session_state.quiz_started:
    if st.button("Start Quiz"):

        q_copy = questions.copy()

        if shuffle_q:
            random.shuffle(q_copy)

        st.session_state.questions = q_copy
        st.session_state.quiz_started = True
        st.rerun()

# QUIZ STARTED
if st.session_state.quiz_started:

    questions = st.session_state.questions

    if not questions:
        st.error("No questions loaded")
        st.stop()

    # MOBILE MODE
    if ui_mode == "Mobile":
        i = st.session_state.current_q
        q = questions[i]

        st.subheader(f"Q{i+1}/{len(questions)}")
        st.write(q["question"])

        # FIX OPTIONS SHUFFLE (ONCE)
        if f"opt_{i}" not in st.session_state:
            opts = q["options"].copy()
            if shuffle_opt:
                random.shuffle(opts)
            st.session_state[f"opt_{i}"] = opts

        options = st.session_state[f"opt_{i}"]

        ans = st.radio("", options, key=f"q_{i}", index=None)

        if ans:
            st.session_state.answers[i] = ans

        col1, col2, col3 = st.columns(3)

        if col1.button("⬅ Prev") and i > 0:
            st.session_state.current_q -= 1
            st.rerun()

        if col2.button("Next ➡") and i < len(questions) - 1:
            st.session_state.current_q += 1
            st.rerun()

        if col3.button("Submit"):
            st.session_state.submitted = True

        st.progress(len(st.session_state.answers) / len(questions))

    # DESKTOP MODE
    else:
        answered = 0

        for i, q in enumerate(questions):
            st.subheader(f"Q{i+1}/{len(questions)}")
            st.write(q["question"])

            if f"opt_{i}" not in st.session_state:
                opts = q["options"].copy()
                if shuffle_opt:
                    random.shuffle(opts)
                st.session_state[f"opt_{i}"] = opts

            options = st.session_state[f"opt_{i}"]

            ans = st.radio("", options, key=f"q_{i}", index=None)

            if ans:
                answered += 1
                st.session_state.answers[i] = ans

            st.markdown("---")

        st.progress(answered / len(questions))

        if st.button("Submit"):
            st.session_state.submitted = True

# RESULT
if st.session_state.submitted:
    score = 0
    st.header("📊 Results")

    for i, q in enumerate(st.session_state.questions):
        st.subheader(f"Q{i+1}: {q['question']}")

        ans = st.session_state.answers.get(i)

        if ans == q["answer"]:
            score += 1
            st.success(f"Your Answer: {ans} ✅ Correct")
        elif ans is None:
            st.warning("Not Answered")
            st.info(f"Correct Answer: {q['answer']}")
        else:
            st.error(f"Your Answer: {ans} ❌")
            st.info(f"Correct Answer: {q['answer']}")

        st.markdown("---")

    st.success(f"Final Score: {score}/{len(st.session_state.questions)}")

    if st.button("Re-attempt"):
        st.session_state.clear()
        st.rerun()