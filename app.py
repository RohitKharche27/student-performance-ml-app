import streamlit as st
import pandas as pd
import pickle
import os
import time

# ---------------- Page config (mobile-first) ----------------
st.set_page_config(
    page_title="Smart Student Analyzer",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------- Attractive Neon Gradient Background CSS ----------------
st.markdown(
    """
    <style>

    /* Full App Background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 40%, #4a00e0 100%);
        background-attachment: fixed;
        color: white !important;
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        padding: 10px;
    }

    /* Header card with glow */
    .header {
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.25);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255,255,255,0.15);
        margin-bottom: 16px;
        animation: fadeIn 1s ease-in-out;
    }
    .header h1 {
        margin: 0;
        font-size: 22px;
        font-weight: 800;
        text-shadow: 0px 0px 6px rgba(255,255,255,0.45);
    }
    .header p {
        margin: 6px 0 0;
        font-size: 13px;
        opacity: 0.95;
    }

    /* Frosted input card */
    .input-card {
        background: rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 0 15px rgba(0,0,0,0.25);
    }

    /* Labels */
    label {
        font-weight: 700 !important;
        font-size: 16px !important;
        color: #ffffff !important;
    }

    /* Input boxes */
    .stNumberInput>div>div>input,
    .stTextInput>div>div>input {
        height: 48px;
        padding: 10px 14px;
        font-size: 17px;
        border-radius: 12px;
        border: none;
        outline: none;
    }

    /* Predict button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg,#00c6ff,#0072ff);
        color: white;
        font-weight: 800;
        padding: 14px;
        border-radius: 14px;
        border: none;
        font-size: 18px;
        box-shadow: 0 8px 25px rgba(0, 140, 255, 0.4);
        transition: 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 10px 30px rgba(0, 140, 255, 0.6);
    }

    /* Result Box */
    .result {
        background: linear-gradient(90deg,#2ecc71,#1abc9c);
        color: white;
        padding: 14px;
        border-radius: 12px;
        font-weight: 900;
        font-size: 19px;
        text-align: center;
        margin-top: 12px;
        box-shadow: 0 0 18px rgba(0,0,0,0.3);
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    """
    <div class="header">
      <h1>📱 Smart Student Analyzer</h1>
      <p>Modern mobile-friendly prediction app with full neon background</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load CSV and Model ----------------
CSV_PATH = "student_scores (1).csv"
MODEL_PATH = "student_score.pkl"

if not os.path.exists(CSV_PATH):
    st.error("❌ CSV file missing! Please upload `student_scores (1).csv`.")
    st.stop()

if not os.path.exists(MODEL_PATH):
    st.error("❌ Model file missing! Upload `student_score.pkl`.")
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
st.subheader("📝 Enter Input Values")

user_inputs = {}

for i, feat in enumerate(feature_cols, start=1):
    nice_label = f"{i}. {feat.replace('_', ' ')}"
    col_data = df[feat].dropna()

    if pd.api.types.is_numeric_dtype(col_data):
        default = float(round(col_data.mean(), 2))
        user_inputs[feat] = st.number_input(nice_label, value=default, step=1.0)
    else:
        default = str(col_data.mode().iloc[0]) if not col_data.mode().empty else ""
        user_inputs[feat] = st.text_input(nice_label, value=default)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict Button ----------------
predict = st.button("🚀 Predict Score")

# ---------------- Prediction Logic ----------------
if predict:
    X = []
    bad = False
    for feat in feature_cols:
        val = user_inputs[feat]
        try:
            X.append(float(val))
        except:
            bad = True
            break

    if bad:
        st.error("⚠️ Please enter valid numeric values.")
    else:
        if expected_features and expected_features != len(X):
            st.error(f"⚠️ Model expects {expected_features} inputs but received {len(X)}.")
        else:
            prog = st.progress(0)
            for i in range(0, 101, 20):
                prog.progress(i)
                time.sleep(0.05)
            prog.empty()

            pred = model.predict([X])[0]

            st.markdown(f"<div class='result'>🏆 Predicted Score: {pred}</div>", unsafe_allow_html=True)

            try:
                score = float(pred)
                if score >= 85:
                    st.success("🎉 Excellent! Great Achievement!")
                    st.balloons()
                elif score >= 70:
                    st.success("✨ Very Good Performance!")
                elif score >= 50:
                    st.info("🙂 Fair — Good chance to improve.")
                else:
                    st.warning("⚠️ Needs Improvement — keep trying!")
            except:
                pass

# ---------------- Footer ----------------
st.markdown("<br><div style='font-size:12px;opacity:0.8;'>Made with ❤️ — Smart Student Analyzer</div>", unsafe_allow_html=True)
