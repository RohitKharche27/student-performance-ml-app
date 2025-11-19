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

# ---------------- Custom CSS ----------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .header-card {
        background: linear-gradient(90deg,#0ea5e9 0%,#7dd3fc 100%);
        color: white;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 8px 30px rgba(13, 71, 161, 0.12);
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 700;
    }

    .card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 6px 18px rgba(20,20,40,0.06);
        margin-bottom: 20px;
    }

    .stButton>button {
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        color: white;
        font-weight: 700;
        padding: 12px 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 20px rgba(124,58,237,0.18);
    }

    .result-badge {
        background: linear-gradient(90deg,#10b981,#34d399);
        color: white;
        padding: 10px 14px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 18px;
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
          <div>Beautiful UI • Smooth Animation • Accurate Model Prediction</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load dataset (hidden from UI) ----------------
csv_path = "student_scores (1).csv"
if not os.path.exists(csv_path):
    st.error("CSV file missing! Please upload it.")
    st.stop()

df = pd.read_csv(csv_path)

# detect target column
cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
feature_cols = [c for c in df.columns if c != target_col]

# ---------------- Load Model ----------------
model_path = "student_score.pkl"
if not os.path.exists(model_path):
    st.error("Model file missing! Upload student_score.pkl.")
    st.stop()

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Model load error: {e}")
    st.stop()

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Input Section ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("✨ Enter Student Details")

cols = st.columns(2)
user_inputs = {}

# smart defaults
defaults = {}
for c in feature_cols:
    coldata = df[c].dropna()
    defaults[c] = float(round(coldata.mean(), 2)) if pd.api.types.is_numeric_dtype(coldata) else ""

# input fields (but names hidden to user, shown as Input 1, Input 2)
for i, feat in enumerate(feature_cols):
    col = cols[i % 2]
    with col:
        label = f"Input {i+1} 🔹"  # <-- names removed
        if pd.api.types.is_numeric_dtype(df[feat]):
            val = st.number_input(label, value=defaults[feat], step=1.0)
        else:
            val = st.text_input(label, value=str(defaults[feat]))
        user_inputs[feat] = val

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict ----------------
center = st.columns([1, 2, 1])[1]
with center:
    predict = st.button("🚀 Predict Score")

if predict:
    X = []
    for c in feature_cols:
        try:
            X.append(float(user_inputs[c]))
        except:
            X.append(user_inputs[c])

    # Feature mismatch check
    if expected_features is not None and expected_features != len(X):
        st.error(
            f"Model expects {expected_features} inputs but received {len(X)}."
        )
    else:
        # loading animation
        bar = st.progress(0)
        for i in range(0, 101, 10):
            bar.progress(i)
            time.sleep(0.03)

        try:
            pred = model.predict([X])[0]

            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:16px;">
                    <div class="result-badge">🏆 {pred}</div>
                    <div style="font-size:18px; font-weight:600;">Predicted Score</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # animations
            try:
                if float(pred) >= 85:
                    st.balloons()
            except:
                pass

        except Exception as e:
            st.error(f"Prediction failed: {e}")

st.markdown("---")
st.caption("Made with ❤️ for a better student performance experience.")
