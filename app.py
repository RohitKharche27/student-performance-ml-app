import streamlit as st
import pandas as pd
import pickle
import os
import time
import numpy as np

# ---------------- Page config ----------------
st.set_page_config(
    page_title="✨ Student Performance Predictor",
    page_icon="🎓",
    layout="wide",
)

# ---------------- Custom CSS (No white boxes + vertical layout) ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #dff4ff 0%, #ffffff 100%);
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .header-card {
        background: linear-gradient(90deg,#06b6d4 0%,#3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.18);
        margin-bottom: 15px;
    }
    .header-title {
        font-size: 30px;
        font-weight: 800;
    }

    /* Remove white background from cards */
    .card {
        background: transparent !important;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* Input box label styling */
    .stNumberInput>div>label {
        font-weight: 700;
        color: #0f172a;
    }

    /* Big Predict button */
    .stButton>button {
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        color: white;
        font-weight: 800;
        padding: 12px 26px;
        border-radius: 12px;
        border: none;
        font-size: 17px;
        box-shadow: 0 8px 20px rgba(124,58,237,0.22);
    }

    /* Result Badge */
    .result-badge {
        background: linear-gradient(90deg,#10b981,#34d399);
        color: white;
        padding: 8px 14px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 20px;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    """
    <div class="header-card">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="font-size:40px;">🎓</div>
            <div>
                <div class="header-title">Student Performance Predictor</div>
                <div>Simple • Clean • Vertical Inputs • No White Boxes</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load dataset (hidden) ----------------
csv_path = "student_scores (1).csv"
if not os.path.exists(csv_path):
    st.error("CSV file missing!")
    st.stop()

df = pd.read_csv(csv_path)

# target detection
cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
feature_cols = [c for c in df.columns if c != target_col]

# ---------------- Load model ----------------
model_path = "student_score.pkl"
if not os.path.exists(model_path):
    st.error("Model file missing!")
    st.stop()

with open(model_path, "rb") as f:
    model = pickle.load(f)

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Inputs (vertical layout) ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📋 Enter Student Details")

user_inputs = {}
defaults = {}

# smart defaults
for c in feature_cols:
    coldata = df[c].dropna()
    defaults[c] = float(round(coldata.mean(), 2)) if pd.api.types.is_numeric_dtype(coldata) else ""

# one-by-one input boxes (vertical)
for i, feat in enumerate(feature_cols):
    label = f"Input {i+1} 🔹"  # names hidden
    if pd.api.types.is_numeric_dtype(df[feat]):
        user_inputs[feat] = st.number_input(label, value=defaults[feat], step=1.0)
    else:
        user_inputs[feat] = st.text_input(label, value=str(defaults[feat]))

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict Button ----------------
btn_center = st.columns([1, 2, 1])[1]
with btn_center:
    predict = st.button("🚀 Predict")

# ---------------- Prediction Logic ----------------
if predict:
    X = []
    for c in feature_cols:
        try:
            X.append(float(user_inputs[c]))
        except:
            X.append(user_inputs[c])

    # feature mismatch
    if expected_features and expected_features != len(X):
        st.error(
            f"Model expects {expected_features} inputs but received {len(X)}."
        )
    else:
        # animated progress
        prog = st.progress(0)
        for p in range(0, 101, 10):
            prog.progress(p)
            time.sleep(0.03)

        pred = model.predict([X])[0]

        # result badge
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:16px;">
                <div class="result-badge">🏆 {pred}</div>
                <div style="font-size:20px; font-weight:700;">Predicted Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # balloons for high score
        try:
            if float(pred) >= 85:
                st.balloons()
        except:
            pass

st.markdown("---")
