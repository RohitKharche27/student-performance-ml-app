import streamlit as st
import pandas as pd
import pickle
import os
import time

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Smart Student Analyzer",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------- Professional Business Gradient CSS ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #0b4f6c 45%, #0b63a6 100%);
        color: #e6f0fb !important;
        font-family: "Inter","Segoe UI","Roboto",sans-serif;
        padding: 14px;
    }

    .header {
        background: rgba(255,255,255,0.04);
        border-left: 4px solid rgba(255,255,255,0.08);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(2,6,23,0.6);
    }
    .header h1 {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        color: white;
    }
    .header p {
        margin: 6px 0 0;
        font-size: 13px;
        color: #cfe8ff;
    }

    .input-card {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 12px;
        box-shadow: 0 6px 25px rgba(2,6,23,0.5);
    }

    label {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #eaf6ff !important;
    }

    .stNumberInput>div>div>input,
    .stTextInput>div>div>input {
        height: 46px;
        padding: 10px 14px;
        background: rgba(255,255,255,0.10);
        color: #ffffff !important;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .result-dark {
        background: rgba(0,0,0,0.55);
        backdrop-filter: blur(6px);
        padding: 14px;
        border-radius: 12px;
        font-size: 18px;
        color: #f1f5f9;
        font-weight: 900;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
        margin-top: 10px;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg,#0b63a6,#0f9cf0);
        color: white;
        font-weight: 800;
        padding: 12px 16px;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        box-shadow: 0 8px 24px rgba(11,99,166,0.28);
    }

    .footer {
        color: rgba(235,245,255,0.85);
        font-size: 12px;
        opacity: 0.95;
        margin-top: 18px;
        text-align:center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    """
    <div class="header">
      <h1>📊 Smart Student Analyzer</h1>
      <p>Professional clean mobile interface</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load CSV and Model ----------------
CSV_PATH = "student_scores (1).csv"
MODEL_PATH = "student_score.pkl"

if not os.path.exists(CSV_PATH):
    st.error("Dataset CSV not found. Upload `student_scores (1).csv`.")
    st.stop()

if not os.path.exists(MODEL_PATH):
    st.error("Model `student_score.pkl` not found.")
    st.stop()

df = pd.read_csv(CSV_PATH)

cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
feature_cols = [c for c in df.columns if c != target_col]

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Input Section ----------------
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.subheader("Enter input values")

user_inputs = {}

for i, feat in enumerate(feature_cols, start=1):
    label = f"{i}. {feat.replace('_',' ')}"
    col_data = df[feat].dropna()

    if pd.api.types.is_numeric_dtype(col_data):
        default = float(round(col_data.mean(), 2))
        user_inputs[feat] = st.number_input(label, value=default, step=1.0)
    else:
        default = str(col_data.mode().iloc[0]) if not col_data.mode().empty else ""
        user_inputs[feat] = st.text_input(label, value=default)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict Button ----------------
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
predict_clicked = st.button("Predict Score")

# ---------------- Prediction Logic ----------------
if predict_clicked:
    X = []
    conversion_error = False

    for feat in feature_cols:
        val = user_inputs[feat]
        try:
            X.append(float(val))
        except:
            conversion_error = True

    if conversion_error:
        st.error("Please enter valid numeric values.")
    else:
        if expected_features and expected_features != len(X):
            st.error(f"Model expects {expected_features} features but got {len(X)}.")
        else:
            prog = st.progress(0)
            for pct in range(0, 101, 25):
                prog.progress(pct)
                time.sleep(0.04)
            prog.empty()

            pred = model.predict([X])[0]

            st.markdown(f"<div class='result-dark'>🏆 Predicted Score: {pred}</div>", unsafe_allow_html=True)

            # Feedback
            try:
                sc = float(pred)
                if sc >= 85:
                    st.success("Excellent result!")
                    st.balloons()
                elif sc >= 70:
                    st.success("Very good performance")
                elif sc >= 50:
                    st.info("Fair — opportunity to improve.")
                else:
                    st.warning("Needs improvement.")
            except:
                pass

# ---------------- Footer ----------------
st.markdown("<div class='footer'>Smart Student Analyzer</div>", unsafe_allow_html=True)
