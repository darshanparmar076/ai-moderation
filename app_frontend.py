import streamlit as st
import requests
import json

# ---------------- CONFIG ----------------
st.set_page_config(page_title="QuizOne AI", layout="wide")

API_URL = "http://localhost:8000"

# ---------------- CUSTOM JSON VIEW ----------------
def pretty_json(data):
    formatted = json.dumps(data, indent=4)
    st.code(formatted, language="json")

# ---------------- HEADER ----------------
st.title("🚀 QuizOne AI Testing Dashboard")
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Control Panel")
endpoint_choice = st.sidebar.radio(
    "Select Service",
    ["🔍 Content Moderation", "📝 Answer Evaluation"]
)

# =========================================================
# 🔍 CONTENT MODERATION
# =========================================================
if endpoint_choice == "🔍 Content Moderation":

    st.header("🔍 Question Moderation")

    if 'mcq_count' not in st.session_state:
        st.session_state.mcq_count = 1

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Question"):
            st.session_state.mcq_count += 1
    with col2:
        if st.button("❌ Remove Last") and st.session_state.mcq_count > 1:
            st.session_state.mcq_count -= 1

    questions_data = []

    for i in range(st.session_state.mcq_count):
        st.subheader(f"Question #{i+1}")

        q_text = st.text_area("Question", key=f"q_{i}")

        colA, colB = st.columns(2)
        options = []

        for j in range(4):
            with (colA if j % 2 == 0 else colB):
                opt = st.text_input(f"Option {chr(65+j)}", key=f"opt_{i}_{j}")
                if opt:
                    options.append(opt)

        questions_data.append({
            "question": q_text,
            "options": options
        })

        st.markdown("---")

    if st.button("🚀 Run Moderation", use_container_width=True):

        payload = {
            "questions": [q for q in questions_data if q["question"]]
        }

        with st.spinner("Checking content..."):
            try:
                res = requests.post(f"{API_URL}/moderate", json=payload)

                if res.status_code == 200:
                    data = res.json()

                    # ✅ JSON VIEW LIKE YOUR IMAGE
                    with st.expander("📄 View Raw JSON Response", expanded=False):
                        pretty_json(data)

                    if data.get("status") == "SAFE":
                        st.success("✅ All questions are safe!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Issues detected")

                        for idx, issue in enumerate(data.get("issues", [])):
                            st.error(f"Issue #{idx+1}: {issue.get('category')}")
                            st.write(f"Type: {issue.get('type')}")
                            st.write(f"Question: {issue.get('questionIndex') + 1}")
                            st.write(f"Text: {issue.get('text')}")
                            st.progress(issue.get("confidence"))

                else:
                    st.error(f"Error: {res.status_code}")

            except Exception as e:
                st.error(f"Connection Failed: {e}")

# =========================================================
# 📝 ANSWER EVALUATION
# =========================================================
else:

    st.header("📝 Answer Evaluation")

    with st.expander("⚙️ Scoring Settings"):
        col1, col2, col3 = st.columns(3)

        with col1:
            full_t = st.slider("Full Marks Threshold", 0, 100, 80)
            full_p = st.number_input("Full Marks %", 0, 100, 100)

        with col2:
            med_t = st.slider("Medium Threshold", 0, 100, 50)
            med_p = st.number_input("Medium %", 0, 100, 50)

        with col3:
            low_t = st.slider("Low Threshold", 0, 100, 20)
            low_p = st.number_input("Low %", 0, 100, 25)

    quiz_settings = {
        "full_threshold": full_t,
        "medium_threshold": med_t,
        "low_threshold": low_t,
        "full_percentage": full_p,
        "medium_percentage": med_p,
        "low_percentage": low_p
    }

    if 'eval_count' not in st.session_state:
        st.session_state.eval_count = 1

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Answer"):
            st.session_state.eval_count += 1
    with col2:
        if st.button("❌ Remove Last") and st.session_state.eval_count > 1:
            st.session_state.eval_count -= 1

    evaluations = []

    for i in range(st.session_state.eval_count):

        st.subheader(f"Evaluation #{i+1}")

        question = st.text_input("Question", key=f"q_eval_{i}")

        colA, colB = st.columns(2)

        with colA:
            model = st.text_area("Model Answer", key=f"model_{i}")

        with colB:
            student = st.text_area("Student Answer", key=f"student_{i}")

        key_points = st.text_input("Key Points (comma separated)", key=f"kp_{i}")
        marks = st.number_input("Max Marks", 1, 100, 5, key=f"marks_{i}")

        kp_list = [k.strip() for k in key_points.split(",") if k.strip()]

        evaluations.append({
            "question": question,
            "model_answer": model,
            "student_answer": student,
            "key_points": kp_list if kp_list else None,
            "max_marks": marks
        })

        st.markdown("---")

    if st.button("🎯 Evaluate", use_container_width=True):

        payload = {
            "quiz_settings": quiz_settings,
            "evaluations": evaluations
        }

        with st.spinner("Evaluating..."):
            try:
                res = requests.post(f"{API_URL}/evaluate-answer-batch", json=payload)

                if res.status_code == 200:
                    data = res.json()

                    st.success("✅ Evaluation Complete")

                    # ✅ JSON VIEW LIKE YOUR IMAGE
                    with st.expander("📄 View Raw JSON Response", expanded=False):
                        pretty_json(data)

                    for idx, result in enumerate(data.get("results", [])):

                        score = result.get("final_marks", 0)
                        sim = result.get("final_similarity", 0)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("Marks", f"{score}/{evaluations[idx]['max_marks']}")

                        with col2:
                            st.metric("Similarity", f"{sim:.2f}%")

                        st.info(result.get("feedback"))
                        st.progress(sim / 100)

                        st.markdown("---")

                else:
                    st.error(f"Error: {res.status_code}")

            except Exception as e:
                st.error(f"Connection Failed: {e}")