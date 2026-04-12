import streamlit as st
import requests
import json

# Set up the page config
st.set_page_config(
    page_title="QuizOne AI - Testing Frontend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        background: #fff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .mcq-container {
        background: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 QuizOne AI Testing Suite")
st.markdown("---")

# Sidebar for API Selection
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.header("Control Panel")
    endpoint_choice = st.radio(
        "Select Service",
        ["🔍 Content Moderation", "📝 Answer Evaluation"],
        index=0
    )
    st.info("Ensure the FastAPI server is running on port 8000")

API_URL = "http://localhost:8000"

# --- Moderation API UI ---
if endpoint_choice == "🔍 Content Moderation":
    st.header("🔍 Question Moderation")
    st.caption("Submit MCQ questions to verify content quality and policy compliance.")

    if 'mcq_count' not in st.session_state:
        st.session_state.mcq_count = 1

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("➕ Add Question"):
            st.session_state.mcq_count += 1
    with col_btn2:
        if st.button("❌ Remove Last") and st.session_state.mcq_count > 1:
            st.session_state.mcq_count -= 1

    questions_data = []
    
    for i in range(st.session_state.mcq_count):
        with st.container():
            st.markdown(f"#### Question #{i+1}")
            with st.expander(f"Edit Content for Question {i+1}", expanded=True):
                q_text = st.text_area("Question Stem", placeholder="e.g., Which planet is known as the Red Planet?", key=f"mod_q_{i}")
                
                opt_cols = st.columns(2)
                options = []
                for j in range(4):
                    with opt_cols[j % 2]:
                        opt = st.text_input(f"Option {chr(65+j)}", placeholder=f"Option {j+1}", key=f"mod_opt_{i}_{j}")
                        if opt:
                            options.append(opt)
                
                questions_data.append({"question": q_text, "options": options})
            st.markdown("---")

    if st.button("🚀 Run Moderation Check", type="primary"):
        if not any(q['question'] for q in questions_data):
            st.warning("Please enter at least one question.")
        else:
            payload = {"questions": [q for q in questions_data if q['question']]}
            with st.spinner("Analyzing content..."):
                try:
                    response = requests.post(f"{API_URL}/moderate", json=payload)
                    if response.status_code == 200:
                        results = response.json()
                        st.success("Analysis Complete!")
                        
                        # Better response display
                        status = results.get("status", "UNKNOWN")
                        if status == "SAFE":
                            st.balloons()
                            st.success("✅ All content is safe!")
                        else:
                            st.warning("⚠️ Content flagged with issues.")
                            for idx, issue in enumerate(results.get("issues", [])):
                                with st.container():
                                    st.markdown(f"""
                                    <div class="status-card" style="border-left-color: #dc3545">
                                        <h4 style="margin:0">Issue #{idx+1}: {issue.get('category')}</h4>
                                        <p style="color:#666"><strong>Type:</strong> {issue.get('type')} (Q#{issue.get('questionIndex', 0) + 1})</p>
                                        <p style="color:#666"><strong>Text:</strong> "{issue.get('text')}"</p>
                                        <p style="color:#666"><strong>Confidence:</strong> {issue.get('confidence'):.2%}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        with st.expander("📄 View Full Raw JSON"):
                            st.json(results)
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

# --- Answer Evaluation API UI ---
elif endpoint_choice == "📝 Answer Evaluation":
    st.header("📝 Smart Answer Evaluation")
    st.caption("AI-powered grading for subjective/short answers based on semantic similarity.")

    # Settings Section
    with st.expander("⚙️ Scoring Configuration", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            full_t = st.slider("Full Marks Threshold", 0, 100, 80, help="Min similarity % for full marks")
            full_p = st.number_input("Full Marks %", 0, 100, 100)
        with c2:
            med_t = st.slider("Medium Marks Threshold", 0, 100, 50)
            med_p = st.number_input("Medium Marks %", 0, 100, 50)
        with c3:
            low_t = st.slider("Low Marks Threshold", 0, 100, 20)
            low_p = st.number_input("Low Marks %", 0, 100, 25)

    quiz_settings = {
        "full_threshold": full_t, "medium_threshold": med_t, "low_threshold": low_t,
        "full_percentage": full_p, "medium_percentage": med_p, "low_percentage": low_p
    }

    if 'eval_count' not in st.session_state:
        st.session_state.eval_count = 1

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("➕ Add Student Answer"):
            st.session_state.eval_count += 1
    with col_btn2:
        if st.button("❌ Remove Last") and st.session_state.eval_count > 1:
            st.session_state.eval_count -= 1

    evaluations = []
    for i in range(st.session_state.eval_count):
        with st.container():
            st.markdown(f"#### Evaluation #{i+1}")
            with st.expander(f"Details for Student {i+1}", expanded=True):
                e_q = st.text_input("Question Text", value="Explain the greenhouse effect.", key=f"ev_q_{i}")
                col_ans1, col_ans2 = st.columns(2)
                with col_ans1:
                    e_m = st.text_area("Reference/Model Answer", placeholder="The correct answer...", key=f"ev_m_{i}")
                with col_ans2:
                    e_s = st.text_area("Student's Submission", placeholder="What the student wrote...", key=f"ev_s_{i}")
                
                col_meta1, col_meta2 = st.columns([3, 1])
                with col_meta1:
                    e_kp = st.text_input("Key Points (comma separated)", placeholder="CO2, Heat trapping, Atmosphere", key=f"ev_kp_{i}")
                with col_meta2:
                    e_marks = st.number_input("Max Marks", 1, 100, 5, key=f"ev_marks_{i}")
                
                key_points_list = [kp.strip() for kp in e_kp.split(',') if kp.strip()]
                evaluations.append({
                    "question": e_q, "model_answer": e_m, "student_answer": e_s,
                    "key_points": key_points_list if key_points_list else None,
                    "max_marks": e_marks
                })
            st.markdown("---")

    if st.button("🎯 Calculate Grades", type="primary"):
        payload = {"quiz_settings": quiz_settings, "evaluations": evaluations}
        with st.spinner("Calculating scores..."):
            try:
                response = requests.post(f"{API_URL}/evaluate-answer-batch", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Grading Complete!")
                    with st.expander("📄 View Raw JSON Response"):
                        st.json(data)
                    
                    for idx, res in enumerate(data.get("results", [])):
                        score = res.get('final_marks', 0)
                        max_m = evaluations[idx]['max_marks']
                        sim = res.get('final_similarity', 0) / 100  # API returns 0-100, we need 0-1
                        
                        # Visual feedback based on score
                        color = "#28a745" if (sim * 100) >= full_t else "#ffc107" if (sim * 100) >= med_t else "#dc3545"
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; border-left: 10px solid {color}; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1)">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin:0">Result for Item {idx+1}</h3>
                                <div style="font-size: 24px; font-weight: bold; color: {color}">
                                    {score} / {max_m} Marks
                                </div>
                            </div>
                            <hr style="margin: 10px 0">
                            <div style="display: flex; gap: 20px; margin-bottom: 10px;">
                                <div style="flex: 1; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                                    <strong>Similarity Score:</strong> {sim:.2%}
                                </div>
                                <div style="flex: 2; background: #f8f9fa; padding: 10px; border-radius: 5px;">
                                    <strong>AI Feedback:</strong> {res.get('feedback', 'No feedback provided.')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"Error {response.status_code}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
