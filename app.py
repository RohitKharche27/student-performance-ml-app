# app.py
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import io
import os
import matplotlib.pyplot as plt
from sklearn.exceptions import NotFittedError

# ----- Page config -----
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----- CSS / Styling -----
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: "Inter", sans-serif;
}

/* background gradient */
[data-testid="stAppViewContainer"]{
    background: linear-gradient(135deg, #f7fbff 0%, #eef6ff 40%, #ffffff 100%);
}

/* card */
.card {
    background: rgba(255,255,255,0.85);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(24,39,75,0.06);
}

/* header */
.header {
    display: flex;
    gap: 16px;
    align-items: center;
}

/* big title */
.title {
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}

.subtitle {
    margin: 0;
    color: #475569;
    font-size: 14px;
}

/* button custom */
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 600;
}

/* input boxes */
input[type="number"] {
    border-radius: 8px;
    padding: 8px;
}

/* small text */
.small {
    color: #64748b;
    font-size: 13px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----- Helper functions -----
def load_model():
    candidates = [
        "/mnt/data/student_score.pkl",  # location where files were uploaded
        "student_score.pkl",
        "Student_model.pkl",
        "student_model.pkl"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    model = pickle.load(f)
                return model, p
            except Exception as e:
                return None, f"FOUND:{p} BUT FAILED TO LOAD: {e}"
    return None, None

def load_csv():
    candidates = [
        "/mnt/data/student_scores (1).csv",
        "/mnt/data/student_scores.csv",
        "student_scores.csv",
        "student_score_data.csv",
        "student_scores (1).csv"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                return df, p
            except Exception as e:
                return None, f"FOUND:{p} BUT FAILED TO READ: {e}"
    return None, None

def safe_predict(model, X):
    try:
        preds = model.predict(X)
        return preds, None
    except Exception as ex:
        return None, str(ex)

# ----- Load model & data (attempt) -----
model, model_info = load_model()
df, csv_info = load_csv()

# ----- Sidebar -----
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-bottom:6px;">🎒 Student Score Predictor</h3>', unsafe_allow_html=True)
    st.markdown('<p class="small">A Streamlit UI to predict student scores from study data.</p>', unsafe_allow_html=True)
    st.markdown('---')
    st.write("Model file status:")
    if model is None:
        if model_info is None:
            st.error("No model file found. Upload a .pkl or place student_score.pkl in project root or /mnt/data.")
        else:
            st.warning(model_info)
        st.file_uploader("Upload model (.pkl)", type=["pkl"], key="model_upload")
    else:
        st.success(f"Loaded model from: `{model_info}`")
        st.download_button("Download model (save copy)", data=open(model_info, "rb").read(), file_name=os.path.basename(model_info))
    st.markdown('---')
    st.write("Dataset")
    if df is None:
        st.info("No dataset found automatically. You can upload a CSV for preview/analysis.")
        uploaded = st.file_uploader("Upload dataset (.csv)", type=["csv"], key="csv_upload")
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                st.success("CSV loaded into session.")
            except Exception as e:
                st.error(f"Failed to read CSV: {e}")
    else:
        st.success(f"Loaded dataset: `{csv_info}`")
        st.write(f"Rows: **{df.shape[0]}**  •  Columns: **{df.shape[1]}**")
        if st.button("Show raw data (sidebar)"):
            st.dataframe(df.head(10))
    st.markdown('<p class="small" style="margin-top:8px;">Tip: If prediction fails due to feature mismatch, re-train or upload a compatible model.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----- Main layout -----
st.markdown('<div class="card header">', unsafe_allow_html=True)
st.markdown('<div style="flex:1">', unsafe_allow_html=True)
st.markdown('<h1 class="title">🎓 Student Score Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Predict student exam score from study features — hours, attendance and assignments.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")  # space

# Input card
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Enter student details")
    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 0.8])

    with col1:
        hours = st.number_input("Hours Studied", value=5.0, min_value=0.0, step=0.5, format="%.2f")
        st.caption("How many hours the student studied per day (average).")
    with col2:
        attendance = st.slider("Attendance (%)", min_value=0, max_value=100, value=85, step=1)
    with col3:
        assignments = st.number_input("Assignments Submitted", value=8, min_value=0, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("Predict Score")

    st.markdown('<hr>', unsafe_allow_html=True)

    # quick sample metrics (if df available)
    if df is not None:
        try:
            # attempt to find numeric columns for basic stats
            num = df.select_dtypes(include=np.number)
            avg_hours = num.get("Hours_Studied", pd.Series([hours])).mean()
            avg_attendance = num.get("Attendance", pd.Series([attendance])).mean()
            avg_assign = num.get("Assignments_Submitted", pd.Series([assignments])).mean()

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Avg Hours (dataset)", f"{avg_hours:.2f}")
            mcol2.metric("Avg Attendance", f"{avg_attendance:.1f}%")
            mcol3.metric("Avg Assignments", f"{avg_assign:.1f}")
        except Exception:
            pass
    else:
        st.info("Upload dataset to show dataset metrics.")

    # Prediction logic
    if predict_btn:
        if model is None:
            st.error("Model not available. Upload or place `student_score.pkl` in the project folder or /mnt/data.")
        else:
            # assemble input
            X = np.array([[hours, attendance, assignments]])
            with st.spinner("Predicting..."):
                # show a progress-like animation
                prog = st.progress(0)
                for i in range(40):
                    prog.progress((i + 1) / 40)
                preds, err = safe_predict(model, X)
                prog.empty()

            if err:
                st.error("Prediction failed.")
                st.write("Error message:")
                st.code(err)
                st.markdown(
                    "<p class='small'>Common cause: the model was trained with a different number of features (e.g. scaling or one-hot encoding)."
                    " If so, re-train model with exactly [Hours_Studied, Attendance, Assignments_Submitted] (in that order) or upload a compatible model.</p>",
                    unsafe_allow_html=True,
                )
            else:
                score = float(preds[0])
                # clamp display
                score = max(0.0, min(100.0, score))
                st.success(f"Predicted Student Score: **{score:.2f} / 100**")

                # visual gauge (simple)
                gauge = st.progress(int(score))
                st.write("")  # spacing
                # show breakdown chart from dataset if available
                if df is not None:
                    st.markdown("#### How this student compares to dataset")
                    try:
                        fig, ax = plt.subplots(figsize=(6, 3.2))
                        ax.scatter(df["Hours_Studied"], df["Score"], alpha=0.7)
                        ax.scatter([hours], [score], color="black", s=80, label="This Student")
                        ax.set_xlabel("Hours Studied")
                        ax.set_ylabel("Score")
                        ax.set_title("Hours Studied vs Score")
                        ax.legend()
                        st.pyplot(fig)
                    except Exception:
                        pass
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")  # spacing

# ----- Data exploration & model diagnostics -----
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Data Preview & Quick Plots")
    if df is None:
        st.info("No dataset available. Upload a CSV in the sidebar to see preview and plots.")
    else:
        st.dataframe(df.head(10))
        # basic plots
        num = df.select_dtypes(include=np.number)
        cols = num.columns.tolist()
        if len(cols) >= 2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Distribution of Scores**")
                fig1, ax1 = plt.subplots()
                ax1.hist(df["Score"], bins=10)
                ax1.set_xlabel("Score")
                ax1.set_ylabel("Count")
                st.pyplot(fig1)
            with col_b:
                st.markdown("**Attendance vs Score**")
                fig2, ax2 = plt.subplots()
                ax2.scatter(df["Attendance"], df["Score"], alpha=0.7)
                ax2.set_xlabel("Attendance")
                ax2.set_ylabel("Score")
                st.pyplot(fig2)
        else:
            st.info("Not enough numeric columns to plot.")

    st.markdown('</div>', unsafe_allow_html=True)

# ----- Footer / credits -----
st.markdown(
    """
    <div style="margin-top:18px; text-align:center;" class="small">
    Built with ❤️ • Streamlit — place your <code>student_score.pkl</code> in project root or <code>/mnt/data</code> for auto load.
    </div>
    """,
    unsafe_allow_html=True,
)
